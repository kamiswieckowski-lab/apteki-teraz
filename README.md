# ✚ Apteki Teraz

[![CI](https://github.com/kamiswieckowski-lab/apteki-teraz/actions/workflows/ci.yml/badge.svg)](https://github.com/kamiswieckowski-lab/apteki-teraz/actions/workflows/ci.yml)
[![Licencja: MIT](https://img.shields.io/badge/licencja-MIT-green.svg)](LICENSE)

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-001 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

**Która apteka jest otwarta teraz, w nocy albo w niedzielę?** Apteki Teraz to otwarta wyszukiwarka
ok. 12 tys. aptek i punktów aptecznych w Polsce, zbudowana na oficjalnym **Rejestrze Aptek**
z portalu [dane.gov.pl](https://dane.gov.pl/pl/dataset/1925,rejestr-aptek).

## Problem społeczny

Kiedy dziecko ma w nocy gorączkę albo w niedzielę kończą się leki na stałe, trzeba szybko znaleźć
otwartą aptekę. Ministerstwo Zdrowia publikuje godziny otwarcia wszystkich aptek, ale tylko jako
plik XLS/CSV z ponad 23 tys. wierszy i 78 kolumnami, którego zwykły człowiek nie przeczyta.
Apteki Teraz zamienia ten plik w prostą wyszukiwarkę:

- **„otwarta teraz”**: filtr uwzględnia dzień tygodnia, niedziele handlowe i niehandlowe oraz święta,
- wyszukiwanie po miejscowości, ulicy, nazwie i kodzie pocztowym, także bez polskich znaków („lodz”),
- filtr na wybrany dzień i godzinę (np. „wtorek 23:30”), apteki całodobowe i ze sprzedażą wysyłkową,
- **statystyki i „białe plamy”**: powiaty, w których nie ma ani jednej apteki całodobowej
  (według rejestru to **286 z 381 powiatów**),
- telefon do apteki jednym kliknięciem i link do mapy.

## Skąd są dane

| | |
|---|---|
| Zbiór | [Rejestr Aptek](https://dane.gov.pl/pl/dataset/1925,rejestr-aptek) (id 1925), dostawca: Ministerstwo Zdrowia |
| Licencja danych | dane publiczne, ponowne wykorzystywanie zgodnie z warunkami dane.gov.pl |
| Aktualizacja | codzienna |
| Pobieranie | `scripts/fetch_data.py` pyta API `api.dane.gov.pl/1.4`, znajduje zasób z generatorem pliku i pobiera CSV |

Dane nie są przechowywane w repozytorium. Każdy może je odtworzyć skryptem. W `tests/fixtures/`
jest tylko 30-wierszowa, zanonimizowana próbka do testów. Szczegóły, jakość danych i
ograniczenia opisuje [docs/dane.md](docs/dane.md).

Z danych **usuwamy dane osobowe** (kierowników aptek, imiona i nazwiska właścicieli będących
osobami fizycznymi). Aplikacja pokazuje tylko informacje potrzebne pacjentowi.

## Szybki start

### Docker (jedna komenda)

```bash
docker compose up --build
```

Otwórz <http://localhost:8000>. Przy pierwszym starcie kontener pobierze dane z dane.gov.pl
(ok. 17 MB, kilka sekund). Dane trafiają do wolumenu, więc kolejne starty są natychmiastowe.
Odświeżenie danych: `docker compose run --rm app python scripts/fetch_data.py`.

### Bez Dockera (Python 3.11+)

```bash
pip install -r requirements.txt
python scripts/fetch_data.py
python -m uvicorn apteki.api:app --app-dir src --port 8000
```

Bez dostępu do internetu: `python scripts/fetch_data.py --sample` (próbka testowa).

### Konfiguracja

Wszystkie ustawienia są w zmiennych środowiskowych, patrz [.env.example](.env.example).
API dane.gov.pl nie wymaga klucza. Projekt nie przechowuje żadnych sekretów.

### Darmowy hosting (Render.com)

1. Zrób fork repozytorium i zaloguj się na <https://render.com> kontem GitHub.
2. Wybierz **New → Web Service**, wskaż repozytorium i ustaw *Runtime: Docker*, plan *Free*.
3. Kliknij *Deploy*. Render zbuduje obraz z `Dockerfile`, a kontener sam pobierze dane i nasłuchuje na `$PORT`.

Ten sam `Dockerfile` działa na Fly.io, Railway czy Google Cloud Run.

## Testy i jakość

```bash
pip install -r requirements-dev.txt
pytest
ruff check . && ruff format --check .
```

CI (GitHub Actions) przy każdym PR uruchamia linter, testy, buduje obraz Dockera i robi smoke test.

## Wydajność i optymalizacja

Pomiar `python scripts/benchmark.py` (lokalnie, 30 powtórzeń, pełne dane: 12 052 apteki):

| Zapytanie | Mediana | p95 | Rozmiar (gzip) |
|---|---|---|---|
| strona główna | 7 ms | 13 ms | 1,4 kB |
| wszystkie apteki, 1. strona | 16 ms | 27 ms | 1,9 kB |
| „otwarte teraz” | 21 ms | 34 ms | 2,0 kB |
| tekst „warszawa marszalkowska” | 26 ms | 34 ms | 0,6 kB |
| wtorek 23:30, mazowieckie | 20 ms | 27 ms | 1,8 kB |
| statystyki | 13 ms | 22 ms | 3,4 kB |

Cały proces ETL (pobranie 17 MB i konwersja do Parquet) trwa ok. 2,5 s.

Zastosowane techniki:

- **ETL do Parquet**: 17 MB CSV → 0,8 MB Parquet (zstd), tylko potrzebne kolumny i wiersze (aktywne apteki publiczne).
- **Godziny jako liczby**: „08:00 - 20:00” zamieniamy w ETL na minuty od północy, więc filtr „otwarta o 23:30” to dwa porównania liczb.
- **Kolumna wyszukiwania** znormalizowana raz w ETL (małe litery, bez polskich znaków), zamiast normalizacji przy każdym zapytaniu.
- **DuckDB w pamięci** zamiast osobnego serwera bazy: dane ładowane raz przy starcie, zapytania kolumnowe, parametryzowane (bez SQL injection).
- **Stronicowanie** (`LIMIT`/`OFFSET`, maks. 100 rekordów) i zwracanie tylko pól potrzebnych w UI.
- **Statystyki liczone raz** przy starcie i trzymane w pamięci.
- **Kompresja gzip** i nagłówki **Cache-Control** (statyczne pliki 24 h, statystyki 1 h, „teraz” bez cache).
- **Frontend bez frameworka i bez etapu budowania**: HTML, CSS i JS mają razem ok. 13 kB. Wyszukiwanie ma debounce (250 ms) i anuluje nieaktualne żądania (`AbortController`).

## Struktura repozytorium

```
src/apteki/        kod aplikacji (ETL, logika godzin, baza, API, frontend w static/)
scripts/           pobieranie danych z API dane.gov.pl, benchmark
tests/             testy pytest + mała próbka danych w fixtures/
docs/              dokumentacja projektu (raport końcowy, lessons learned, dane, architektura)
.github/           CI, szablony zgłoszeń i pull requestów
```

## Dokumentacja

- [Rejestr dokumentów (ISO 10013)](docs/rejestr-dokumentow.md)
- [Plan projektu](docs/plan-projektu.md)
- [Dane i ich jakość](docs/dane.md)
- [Architektura](docs/architektura.md)
- [Raport końcowy (ISO 21513)](docs/raport-koncowy.md)
- [Lessons learned (PMI)](docs/lessons-learned.md)

## Współtworzenie

Zgłoszenia błędów i pull requesty są mile widziane. Zasady opisuje [CONTRIBUTING.md](CONTRIBUTING.md),
a obowiązujące normy zachowania [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Zastrzeżenie

Godziny otwarcia pochodzą z rejestru prowadzonego przez wojewódzkich inspektorów farmaceutycznych
i mogą być nieaktualne. Przed wyjściem zadzwoń do apteki. W nagłych przypadkach dzwoń pod **112**.

## Licencja

Kod udostępniamy na licencji [MIT](LICENSE).

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
