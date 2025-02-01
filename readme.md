# LLM Proxy z GUI do zarządzania słowami kluczowymi

## O projekcie
LLM Proxy to narzędzie umożliwiające inteligentne przekierowywanie zapytań między llama.cpp a Flowise na podstawie słów kluczowych. Wyposażone jest w prosty interfejs webowy do zarządzania regułami przekierowań.

## Główne funkcje
- Przekierowanie zapytań do llama.cpp lub Flowise na podstawie słów kluczowych
- Interfejs webowy do zarządzania słowami kluczowymi
- Zachowanie kontekstu rozmowy dla llama.cpp
- Izolacja kontekstu dla zapytań do Flowise
- Automatyczne usuwanie znaczników emocji [xxx] dla Flowise
- Persystentne przechowywanie konfiguracji w SQLite
- Pełna konteneryzacja w Docker

## Wymagania
- Docker i Docker Compose
- Działający serwer llama.cpp
- Działający serwer Flowise
- Python 3.9+

## Instalacja
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

## Dostępne endpointy
- GUI: `http://localhost:5555` - interfejs zarządzania słowami kluczowymi
- API: `http://localhost:8444` - endpointy proxy dla llama.cpp i Flowise

## Struktura projektu
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

## Użycie API
### Dodawanie słowa kluczowego
```bash
curl -X POST http://localhost:8444/api/keywords \
  -H "Content-Type: application/json" \
  -d '{"keyword": "temperatura", "flowise_id": "your-flow-id", "description": "Zapytanie o temperaturę"}'
```

### Wysyłanie zapytania
```bash
curl -X POST http://localhost:8444/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Jaka jest temperatura?"}]}'
```

## Zarządzanie przez GUI
1. Otwórz `http://localhost:5555` w przeglądarce
2. Dodaj, edytuj lub usuń słowa kluczowe
3. Każde słowo kluczowe wymaga:
   - Frazy do wykrycia
   - ID przepływu Flowise
   - Opcjonalnego opisu

## Jak to działa
1. Dla każdego zapytania system sprawdza, czy w tekście występuje któreś ze zdefiniowanych słów kluczowych
2. Jeśli znajdzie dopasowanie:
   - Przekazuje oczyszczone zapytanie (bez kontekstu i znaczników emocji) do odpowiedniego przepływu Flowise
3. Jeśli nie znajdzie dopasowania:
   - Przekazuje pełne zapytanie (z kontekstem) do llama.cpp
   - Zachowuje historię rozmowy

## Rozwiązywanie problemów
### Najczęstsze problemy
1. Błąd połączenia z llama.cpp lub Flowise
   - Sprawdź czy usługi są uruchomione
   - Zweryfikuj adresy URL w konfiguracji
   
2. Problemy z bazą danych
   - Sprawdź uprawnienia do katalogu /data
   - Zweryfikuj czy volume Docker jest poprawnie zamontowany

## Licencja
MIT

## Współtwórcy
- [Twoje imię/nick]
- [Inni współtwórcy]
