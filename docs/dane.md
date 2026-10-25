# Dane i ich jakość

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-012 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

## Źródło

| Pole | Wartość |
|---|---|
| Portal | [dane.gov.pl](https://dane.gov.pl) |
| Zbiór | [Rejestr Aptek](https://dane.gov.pl/pl/dataset/1925,rejestr-aptek), id `1925` |
| Dostawca | Ministerstwo Zdrowia (Platforma Rejestrów Medycznych, e-Zdrowie) |
| Zasób | id `1775964`, „Link do API umożliwiającego wygenerowanie zbioru danych zawierającego Rejestr aptek” |
| Częstotliwość aktualizacji | codziennie |
| Format | generator `rejestry.ezdrowie.gov.pl/api/ra/filegenerator/getxls`, ten sam generator udostępnia `getcsv` |
| CSV | UTF-8 z BOM, separator `\|`, puste wartości jako `""`, 78 kolumn, ok. 24 tys. wierszy, ok. 17 MB |

## Jak pobieramy dane

`scripts/fetch_data.py`:

1. `GET https://api.dane.gov.pl/1.4/datasets/1925/resources`: lista zasobów zbioru,
2. wybór zasobu, którego pole `link` wskazuje na generator pliku (`filegenerator`),
3. pobranie wariantu CSV (lżejszy i prostszy w parsowaniu niż XLS w starym formacie BIFF),
4. ETL (`src/apteki/etl.py`) → `data/apteki.parquet`, metadane (data danych, liczba rekordów) → `data/meta.json`.

Adres pliku można nadpisać zmienną `CSV_URL`. Dane nie są wersjonowane w Git.

## Przetwarzanie (ETL)

| Krok | Opis |
|---|---|
| Filtrowanie | `stan_apteki = AKTYWNA` oraz rodzaj „apteka ogólnodostępna” lub „punkt apteczny”. Apteki szpitalne i zakładowe są niedostępne dla pacjentów, więc je pomijamy |
| Dane osobowe | usuwamy kierownika, zastępcę, imię i nazwisko, NIP, REGON i KRS właściciela. Nazwy właściciela używamy tylko wtedy, gdy apteka nie ma własnej nazwy, a właściciel nie jest osobą fizyczną |
| Godziny | `"08:00 - 20:00"` → `o_pn = 480`, `c_pn = 1200` (minuty od północy). `"całodobowo"` → 0–1440. Godziny przez północ są obcinane do 24:00. Wpisy nieczytelne traktujemy jak brak danych |
| Normalizacja | województwa małymi literami z łącznikiem („kujawsko pomorskie” → „kujawsko-pomorskie”), miejscowości z WIELKICH LITER → „Wielkie Litery”, adres sklejany z typu ulicy, nazwy, numeru i lokalu |
| Wyszukiwanie | kolumna `szukaj` = nazwa + miejscowość + adres + kod + gmina + powiat, małe litery, bez polskich znaków |

## Kalendarz („otwarta teraz”)

Rejestr podaje godziny osobno dla dni pn–sb, niedzieli handlowej i niedzieli niehandlowej.
Moduł `hours.py` wybiera właściwy zestaw:

- dni robocze pn–sb według dnia tygodnia,
- **święta ustawowe** (w tym Wigilia od 2025 r.) traktujemy jak niedzielę niehandlową,
- **niedziele handlowe**: ostatnia niedziela stycznia, kwietnia, czerwca i sierpnia, niedziela przed
  Wielkanocą oraz trzy niedziele przed Wigilią.

## Jakość danych (stan na 2026-10-24)

| Miara | Wartość |
|---|---|
| Wszystkie rekordy w rejestrze | 24 014 |
| Aktywne | 13 706 |
| Aktywne apteki ogólnodostępne i punkty apteczne (po ETL) | **12 052** (w tym 1 103 punkty apteczne) |
| Brak godzin w poniedziałek | 527 (4,4%) |
| Brak godzin w sobotę | 1 705 (14%), część aptek jest w sobotę zamknięta |
| Podane godziny w niedzielę niehandlową | **242 (2%)** |
| Kolumna „niedziela handlowa” wypełniona | **0**: kolumna jest w całości pusta |
| Nieczytelne wpisy godzin | 2 (np. `08:00 - 16;0`) |
| Niespójny zapis województwa | 17 rekordów („kujawsko pomorskie” bez łącznika) |
| Apteki całodobowe (pn–sb) | 151 |
| Powiaty bez apteki całodobowej | 286 z 381 |

### Wnioski i ograniczenia

- **Niedziele są słabo opisane w rejestrze.** Tylko 2% aptek podaje godziny niedzielne, a kolumna
  „niedziela handlowa” jest zawsze pusta. W niedzielę handlową używamy więc godzin
  „niedzieli niehandlowej”. W rzeczywistości otwartych aptek jest więcej, bo wiele z nich ma dyżury
  ustalane uchwałą powiatu, a tych danych nie ma w rejestrze centralnym.
- **Brak geolokalizacji.** Zamiast mapy podajemy link do wyszukiwania adresu w mapach.
- Godziny w rejestrze aktualizują wojewódzkie inspektoraty farmaceutyczne i mogą się opóźniać.
  Interfejs przypomina, żeby przed wyjściem zadzwonić do apteki.

## Próbka testowa

`tests/fixtures/apteki_sample.csv`: 30 rekordów wylosowanych z prawdziwego rejestru (aktywne,
nieaktywne, szpitalne, całodobowe, niedzielne, z celowo uszkodzonym wpisem godzin). Dane osobowe
i kontaktowe zastąpiono fikcyjnymi (telefony `+48 12 000 00 NN`, e-maile `@example.com`).

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
