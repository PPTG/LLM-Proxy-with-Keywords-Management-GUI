from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import logging
import sys
import os
from typing import Dict, Any
import sqlite3
from pydantic import BaseModel

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LLAMA_URL = "http://192.168.1.166:8988"  # URL do llama.cpp
FLOWISE_URL = "http://192.168.1.166:3000"
TIMEOUT_CONFIG = httpx.Timeout(timeout=300.0)
DATABASE_URL = os.getenv('DATABASE_URL', '/data/keywords.db')

os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS keywords
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  keyword TEXT NOT NULL,
                  flowise_id TEXT NOT NULL,
                  description TEXT)''')
    conn.commit()
    conn.close()

init_db()

class KeywordRule(BaseModel):
    keyword: str
    flowise_id: str
    description: str = ""

@app.post("/api/keywords")
async def create_keyword(rule: KeywordRule):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('INSERT INTO keywords (keyword, flowise_id, description) VALUES (?, ?, ?)',
              (rule.keyword, rule.flowise_id, rule.description))
    conn.commit()
    id = c.lastrowid
    conn.close()
    return {"id": id, **rule.dict()}

@app.get("/api/keywords")
async def get_keywords():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('SELECT id, keyword, flowise_id, description FROM keywords')
    keywords = [{"id": row[0], "keyword": row[1], "flowise_id": row[2], "description": row[3]} 
                for row in c.fetchall()]
    conn.close()
    return keywords

@app.put("/api/keywords/{keyword_id}")
async def update_keyword(keyword_id: int, rule: KeywordRule):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('UPDATE keywords SET keyword=?, flowise_id=?, description=? WHERE id=?',
              (rule.keyword, rule.flowise_id, rule.description, keyword_id))
    conn.commit()
    conn.close()
    return {"id": keyword_id, **rule.dict()}

@app.delete("/api/keywords/{keyword_id}")
async def delete_keyword(keyword_id: int):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('DELETE FROM keywords WHERE id=?', (keyword_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/chat")
async def chat(request: Request):
    print("Otrzymano zapytanie chat", flush=True)
    try:
        data = await request.json()
        messages = data.get("messages", [])
        last_message = messages[-1].get("content", "").lower() if messages else ""
        
        # Sprawdzanie słów kluczowych z bazy danych
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('SELECT keyword, flowise_id FROM keywords')
        keywords = c.fetchall()
        conn.close()

        for keyword, flowise_id in keywords:
            if keyword.lower() in last_message:
                try:
                    async with httpx.AsyncClient(timeout=TIMEOUT_CONFIG) as client:
                        flowise_response = await client.post(
                            f"{FLOWISE_URL}/api/v1/prediction/{flowise_id}",
                            json={"question": last_message}
                        )
                        return StreamingResponse(
                            iter([json.dumps({
                                "model": "flowise",
                                "message": {
                                    "role": "assistant",
                                    "content": flowise_response.json().get("text", "Brak odpowiedzi")
                                },
                                "done": True
                            }) + "\n"]),
                            media_type="application/x-ndjson"
                        )
                except Exception as e:
                    print(f"Błąd Flowise: {str(e)}", flush=True)

        # Przygotowanie wiadomości w formacie chat/completions
        llama_request = {
            "model": "llama2",
            "messages": messages,
            "temperature": 0.7,
            "stream": True
        }

        print(f"Wysyłanie do llama.cpp: {llama_request}", flush=True)

        async def generate():
            async with httpx.AsyncClient(timeout=TIMEOUT_CONFIG) as client:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
                async with client.stream("POST", f"{LLAMA_URL}/v1/chat/completions", 
                                       json=llama_request, headers=headers) as response:
                    buffer = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            line = line[6:]  # Usuń "data: " z początku linii
                            if line.strip() == "[DONE]":
                                continue
                            try:
                                completion_chunk = json.loads(line)
                                if "choices" in completion_chunk:
                                    content = completion_chunk["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield json.dumps({
                                            "model": "llama",
                                            "message": {
                                                "role": "assistant",
                                                "content": content
                                            },
                                            "done": completion_chunk["choices"][0].get("finish_reason") is not None
                                        }) + "\n"
                            except json.JSONDecodeError as e:
                                print(f"Błąd dekodowania JSON: {line}", flush=True)
                                continue

        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson"
        )
            
    except Exception as e:
        print(f"BŁĄD GŁÓWNY: {str(e)}", flush=True)
        logger.error("Szczegóły błędu:", exc_info=True)
        return StreamingResponse(
            iter([json.dumps({"error": str(e)}) + "\n"]),
            media_type="application/x-ndjson"
        )

import re  # Dodaj na początku pliku

@app.post("/completion")
async def completion(request: Request):
    print("Otrzymano zapytanie completion", flush=True)
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        
        # Wyciągamy tylko najnowszy prompt
        last_prompt = prompt.split("User:")[-1].strip() if "User:" in prompt else prompt
        
        # Usuwamy znaczniki emocji [xxx]
        clean_prompt = re.sub(r'\[.*?\]', '', last_prompt).strip()
        print(f"Oczyszczony prompt: {clean_prompt}", flush=True)
        
        # Sprawdzanie słów kluczowych z bazy danych
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('SELECT keyword, flowise_id FROM keywords')
        keywords = c.fetchall()
        conn.close()

        for keyword, flowise_id in keywords:
            if keyword.lower() in clean_prompt.lower():
                try:
                    async with httpx.AsyncClient(timeout=TIMEOUT_CONFIG) as client:
                        flowise_response = await client.post(
                            f"{FLOWISE_URL}/api/v1/prediction/{flowise_id}",
                            json={"question": clean_prompt}
                        )
                        response_text = flowise_response.json().get("text", "Brak odpowiedzi")
                        return StreamingResponse(
                            iter([json.dumps({
                                "content": response_text,
                                "stop": True
                            }) + "\n"]),
                            media_type="application/x-ndjson"
                        )
                except Exception as e:
                    print(f"Błąd Flowise: {str(e)}", flush=True)

        # Przygotowanie zapytania do llama.cpp chat/completions
        messages = [{"role": "user", "content": prompt}]
        llama_request = {
            "model": "llama2",
            "messages": messages,
            "temperature": 0.7,
            "stream": True
        }

        print(f"Wysyłanie do llama.cpp: {llama_request}", flush=True)

        async def generate():
            async with httpx.AsyncClient(timeout=TIMEOUT_CONFIG) as client:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
                async with client.stream("POST", f"{LLAMA_URL}/v1/chat/completions", 
                                       json=llama_request, headers=headers) as response:
                    buffer = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            line = line[6:]  # Usuń "data: " z początku linii
                            if line.strip() == "[DONE]":
                                continue
                            try:
                                completion_chunk = json.loads(line)
                                if "choices" in completion_chunk:
                                    content = completion_chunk["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield json.dumps({
                                            "content": content,
                                            "stop": completion_chunk["choices"][0].get("finish_reason") is not None
                                        }) + "\n"
                            except json.JSONDecodeError as e:
                                print(f"Błąd dekodowania JSON: {line}", flush=True)
                                continue

        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson"
        )

    except Exception as e:
        print(f"BŁĄD GŁÓWNY: {str(e)}", flush=True)
        logger.error("Szczegóły błędu:", exc_info=True)
        return StreamingResponse(
            iter([json.dumps({"error": str(e)}) + "\n"]),
            media_type="application/x-ndjson"
        )
