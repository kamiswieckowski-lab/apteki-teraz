# Architektura

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-013 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

## Przegląd

```
 api.dane.gov.pl ──(1) lista zasobów──┐
                                      ▼
 rejestry.ezdrowie.gov.pl ──(2) CSV──► scripts/fetch_data.py ──► etl.py ──► data/apteki.parquet
                                                                                   │ (3) start
                                                                                   ▼
 przeglądarka ◄──── HTML/CSS/JS (static) ◄──── FastAPI (api.py) ◄──── DuckDB w pamięci (db.py)
              ────► /api/search, /api/stats, /api/meta ──►
```

## Komponenty

| Moduł | Odpowiedzialność |
|---|---|
| `scripts/fetch_data.py` | Znalezienie zasobu w API dane.gov.pl, pobranie CSV, uruchomienie ETL, zapis metadanych |
| `src/apteki/etl.py` | Filtrowanie, anonimizacja, parsowanie godzin, normalizacja, zapis Parquet (przez DuckDB) |
| `src/apteki/hours.py` | Parsowanie godzin, Wielkanoc, święta, niedziele handlowe, wybór dnia |
| `src/apteki/db.py` | Ładowanie Parquet do DuckDB, wyszukiwanie z parametrami, statystyki liczone przy starcie |
| `src/apteki/api.py` | Endpointy HTTP, walidacja parametrów, gzip, nagłówki cache, serwowanie frontendu |
| `src/apteki/static/` | Interfejs w czystym HTML/CSS/JS, bez etapu budowania |
| `src/apteki/config.py` | Konfiguracja wyłącznie ze zmiennych środowiskowych |

## API

| Endpoint | Parametry | Opis |
|---|---|---|
| `GET /api/search` | `q`, `wojewodztwo`, `kiedy` (`teraz` / `pn`…`nn`), `godzina` (`HH:MM`), `calodobowa`, `wysylkowa`, `limit` (1–100), `offset` | Lista aptek + `total` |
| `GET /api/stats` | | Statystyki: Polska, województwa, powiaty bez apteki całodobowej |
| `GET /api/meta` | | Liczba aptek, lista województw, etykiety dni, metadane źródła |
| `GET /health` | | Healthcheck |
| `GET /docs` | | Automatyczna dokumentacja OpenAPI (Swagger UI) |

## Decyzje projektowe

| Decyzja | Uzasadnienie |
|---|---|
| Python + FastAPI | Prosty, czytelny kod, automatyczna walidacja i dokumentacja OpenAPI |
| DuckDB zamiast PostgreSQL | 12 tys. rekordów mieści się w pamięci, nie trzeba stawiać serwera bazy, natywnie czyta Parquet |
| Parquet jako format pośredni | 20× mniejszy niż CSV, typowane kolumny, szybkie ładowanie |
| Godziny jako liczby całkowite | Filtr „otwarta o 23:30” to proste porównanie, bez parsowania tekstu w zapytaniu |
| Frontend bez frameworka | ok. 13 kB, zero zależności i zero etapu budowania, szybkie pierwsze ładowanie |
| Dane pobierane przy starcie kontenera | Repozytorium bez dużych plików, zawsze świeże dane, jedna komenda uruchomienia |

## Bezpieczeństwo i prywatność

- zapytania SQL są parametryzowane, a nazwy kolumn dni pochodzą z białej listy,
- walidacja parametrów (długość `q`, wzorzec `godzina`, zakres `limit`),
- dane osobowe usuwane w ETL, kontener działa jako użytkownik bez uprawnień roota,
- wszystkie wartości z danych są escapowane we frontendzie (ochrona przed XSS).

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
