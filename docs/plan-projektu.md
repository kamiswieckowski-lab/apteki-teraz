# Plan projektu

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-011 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

## Cel

W ciągu tygodnia zbudować otwartoźródłową aplikację na danych z dane.gov.pl, która rozwiązuje
konkretny problem społeczny. Wybrany problem: **trudno sprawdzić, która apteka jest otwarta w nocy,
w niedzielę lub w święto.**

## Zakres

| W zakresie | Poza zakresem |
|---|---|
| Pobieranie Rejestru Aptek przez API dane.gov.pl | Mapa z geolokalizacją (rejestr nie ma współrzędnych) |
| Wyszukiwarka z filtrem „otwarta teraz” / dzień + godzina | Dostępność konkretnych leków |
| Statystyki dostępności per województwo i powiat | Dyżury aptek ustalane przez starostwa (brak danych centralnych) |
| Uruchomienie jedną komendą, CI, dokumentacja | Aplikacja mobilna |

## Harmonogram i kamienie milowe

| # | Kamień milowy | Kryterium ukończenia | Termin planowany |
|---|---|---|---|
| M1 | Wybór problemu i zbioru danych | Zbiór sprawdzony w API, znane kolumny i format | dzień 1 |
| M2 | Pipeline danych | Skrypt pobiera dane, ETL tworzy Parquet | dzień 2 |
| M3 | API + frontend | Wyszukiwanie i statystyki działają lokalnie | dzień 3–4 |
| M4 | Jakość | Testy, linter, CI zielone | dzień 5 |
| M5 | Wdrożenie i dokumentacja | Docker, README, raport, lessons learned | dzień 6 |
| M6 | Demo | Prezentacja działającej aplikacji | dzień 7 |

## Założenia wydajnościowe

- odpowiedź API < 100 ms (mediana) na pełnych danych,
- strona główna < 50 kB łącznie,
- pełne odświeżenie danych < 1 min.

## Ryzyka

| Ryzyko | Prawdopodobieństwo | Wpływ | Reakcja |
|---|---|---|---|
| Format pliku źródłowego się zmieni | średnie | wysoki | Wyszukiwanie zasobu po API, test na próbce, łatwa zmiana mapowania w `etl.py` |
| Niekompletne godziny otwarcia | wysokie | średni | Jawna informacja w UI i dokumentacji, statystyki jakości danych |
| Dane osobowe w rejestrze | pewne | wysoki | Usuwanie kolumn osobowych w ETL, test to weryfikujący |
| Brak Dockera u oceniającego | średnie | średni | Alternatywne uruchomienie przez `pip` + `uvicorn` |

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
