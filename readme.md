# LLM Proxy with Keywords Management GUI

[English](#english) | [Polski](#polski)

<a name="english"></a>
## English
### About
LLM Proxy is a tool that enables intelligent request routing between llama.cpp and Flowise based on keywords. It features a simple web interface for managing routing rules.

### Key Features
- Request routing between llama.cpp and Flowise based on keywords
- Web interface for keyword management
- Conversation context preservation for llama.cpp
- Context isolation for Flowise requests
- Automatic removal of emotion tags [xxx] for Flowise
- Persistent configuration storage in SQLite
- Full Docker containerization

### Requirements
- Docker and Docker Compose
- Running llama.cpp server
- Running Flowise server
- Python 3.9+

### Installation
1. Clone the repository
```bash
git clone https://github.com/your-username/llm-proxy.git
cd llm-proxy
```

2. Configure environment variables in docker-compose.yml
```yaml
environment:
  - LLAMA_URL=http://your-llama-server:8988
  - FLOWISE_URL=http://your-flowise-server:3000
```

3. Run the application
```bash
docker compose up --build
```

### Available Endpoints
- GUI: `http://localhost:5555` - keyword management interface
- API: `http://localhost:8444` - proxy endpoints for llama.cpp and Flowise

### Project Structure
```
/
├── app.py            # Main FastAPI application file
├── gui.py           # Flask application for web interface
├── requirements.txt  # Python dependencies
├── Dockerfile       # Docker image configuration
├── docker-compose.yml # Services configuration
└── templates/       # HTML templates for GUI
    └── index.html   # Main interface template
```

### API Usage
#### Adding a keyword
```bash
curl -X POST http://localhost:8444/api/keywords \
  -H "Content-Type: application/json" \
  -d '{"keyword": "temperature", "flowise_id": "your-flow-id", "description": "Temperature query"}'
```

#### Sending a query
```bash
curl -X POST http://localhost:8444/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is the temperature?"}]}'
```

### GUI Management
1. Open `http://localhost:5555` in your browser
2. Add, edit, or delete keywords
3. Each keyword requires:
   - Detection phrase
   - Flowise flow ID
   - Optional description

### How it Works
1. For each query, the system checks if any defined keywords are present in the text
2. If a match is found:
   - Forwards the cleaned query (without context and emotion tags) to the appropriate Flowise flow
3. If no match is found:
   - Forwards the complete query (with context) to llama.cpp
   - Maintains conversation history

### Troubleshooting
Common issues:
1. Connection error with llama.cpp or Flowise
   - Check if services are running
   - Verify URLs in configuration
   
2. Database issues
   - Check /data directory permissions
   - Verify Docker volume mounting

---

<a name="polski"></a>
## Polski
### O projekcie
LLM Proxy to narzędzie umożliwiające inteligentne przekierowywanie zapytań między llama.cpp a Flowise na podstawie słów kluczowych. Wyposażone jest w prosty interfejs webowy do zarządzania regułami przekierowań.

### Główne funkcje
- Przekierowanie zapytań do llama.cpp lub Flowise na podstawie słów kluczowych
- Interfejs webowy do zarządzania słowami kluczowymi
- Zachowanie kontekstu rozmowy dla llama.cpp
- Izolacja kontekstu dla zapytań do Flowise
- Automatyczne usuwanie znaczników emocji [xxx] dla Flowise
- Persystentne przechowywanie konfiguracji w SQLite
- Pełna konteneryzacja w Docker

### Wymagania
- Docker i Docker Compose
- Działający serwer llama.cpp
- Działający serwer Flowise
- Python 3.9+

### Instalacja
1. Sklonuj repozytorium
```bash
git clone https://github.com/your-username/llm-proxy.git
cd llm-proxy
```

2. Skonfiguruj zmienne środowiskowe w docker-compose.yml
```yaml
environment:
  - LLAMA_URL=http://your-llama-server:8988
  - FLOWISE_URL=http://your-flowise-server:3000
```

3. Uruchom aplikację
```bash
docker compose up --build
```

### Dostępne endpointy
- GUI: `http://localhost:5555` - interfejs zarządzania słowami kluczowymi
- API: `http://localhost:8444` - endpointy proxy dla llama.cpp i Flowise

### Struktura projektu
```
/
├── app.py            # Główny plik aplikacji FastAPI
├── gui.py           # Aplikacja Flask do interfejsu webowego
├── requirements.txt  # Zależności Pythona
├── Dockerfile       # Konfiguracja obrazu Docker
├── docker-compose.yml # Konfiguracja usług
└── templates/       # Szablony HTML dla GUI
    └── index.html   # Główny szablon interfejsu
```

### Użycie API
#### Dodawanie słowa kluczowego
```bash
curl -X POST http://localhost:8444/api/keywords \
  -H "Content-Type: application/json" \
  -d '{"keyword": "temperatura", "flowise_id": "your-flow-id", "description": "Zapytanie o temperaturę"}'
```

#### Wysyłanie zapytania
```bash
curl -X POST http://localhost:8444/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Jaka jest temperatura?"}]}'
```

### Zarządzanie przez GUI
1. Otwórz `http://localhost:5555` w przeglądarce
2. Dodaj, edytuj lub usuń słowa kluczowe
3. Każde słowo kluczowe wymaga:
   - Frazy do wykrycia
   - ID przepływu Flowise
   - Opcjonalnego opisu

### Jak to działa
1. Dla każdego zapytania system sprawdza, czy w tekście występuje któreś ze zdefiniowanych słów kluczowych
2. Jeśli znajdzie dopasowanie:
   - Przekazuje oczyszczone zapytanie (bez kontekstu i znaczników emocji) do odpowiedniego przepływu Flowise
3. Jeśli nie znajdzie dopasowania:
   - Przekazuje pełne zapytanie (z kontekstem) do llama.cpp
   - Zachowuje historię rozmowy

### Rozwiązywanie problemów
Najczęstsze problemy:
1. Błąd połączenia z llama.cpp lub Flowise
   - Sprawdź czy usługi są uruchomione
   - Zweryfikuj adresy URL w konfiguracji
   
2. Problemy z bazą danych
   - Sprawdź uprawnienia do katalogu /data
   - Zweryfikuj czy volume Docker jest poprawnie zamontowany

---

## License / Licencja
MIT

## Contributors / Współtwórcy
- [Your name/nick] / [Twoje imię/nick]
- [Other contributors] / [Inni współtwórcy]
