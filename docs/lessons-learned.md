# Lessons learned

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-015 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

Dokument przygotowano według podejścia PMI (PMBOK, proces *Manage Project Knowledge*, rejestr
*lessons learned*). Każda lekcja ma kategorię, opis, skutek i rekomendację.

## Co zadziałało

| # | Kategoria | Lekcja | Skutek |
|---|---|---|---|
| 1 | Dane | Zanim wybraliśmy temat, sprawdziliśmy kilka zbiorów bezpośrednio w API dane.gov.pl (żłobki, ceny mieszkań, apteki) | Wybraliśmy zbiór kompletny, ogólnopolski i codziennie aktualizowany. Uniknęliśmy zbiorów rozproszonych w tysiącach plików |
| 2 | Technologia | DuckDB + Parquet zamiast serwera bazy danych | Zero konfiguracji, odpowiedzi ok. 20 ms, ETL w 2,5 s |
| 3 | Wydajność | Przeniesienie pracy do ETL (godziny jako minuty, znormalizowana kolumna wyszukiwania) | Zapytania są proste i szybkie |
| 4 | Jakość | Testy na małej, zanonimizowanej próbce prawdziwych danych | CI działa bez sieci, a testy łapią prawdziwe przypadki brzegowe (np. `08:00 - 16;0`) |
| 5 | Prywatność | Anonimizacja jako jawny krok ETL z testem | Brak ryzyka publikacji danych osobowych |
| 6 | Wdrożenie | Kontener pobiera dane przy pierwszym starcie | Repozytorium bez dużych plików, jedna komenda uruchomienia |

## Co nie zadziałało

| # | Kategoria | Problem | Skutek | Jak sobie poradziliśmy |
|---|---|---|---|---|
| 1 | Dane | Kolumna „niedziela handlowa” jest całkowicie pusta, a godziny niedzielne podaje tylko 2% aptek | Najważniejszy filtr ma ograniczoną kompletność | Uzupełnienie z kolumny niedzieli niehandlowej, ostrzeżenie w UI, opis w `docs/dane.md` |
| 2 | Dane | Brak współrzędnych geograficznych | Nie da się zrobić mapy ani wyszukiwania „najbliższa apteka” | Link do map na podstawie adresu |
| 3 | Dane | Zasób na dane.gov.pl to XLS w starym formacie BIFF (32 MB) | Potrzebna dodatkowa biblioteka, wolniejszy odczyt | Ten sam generator udostępnia CSV (17 MB), więc skrypt korzysta z CSV |
| 4 | Narzędzia | Na Windowsie `localhost` rozwiązuje się najpierw do IPv6, co dodaje ok. 0,2–2 s do każdego żądania | Pierwszy benchmark dał fałszywe, bardzo złe wyniki | Pomiar na `127.0.0.1` (domyślny adres w skrypcie benchmarku) |
| 5 | Proces | Pierwsza wersja ETL miała typy kolumn w złej kolejności | Błąd konwersji przy zapisie Parquet | Typy generowane z jednej listy kolumn (`COLUMNS`), test sprawdzający schemat |

## Co zrobilibyśmy inaczej

1. **Na samym początku przygotowalibyśmy profil jakości danych** (procent wypełnienia każdej kolumny). Problem pustych godzin niedzielnych wyszedłby na etapie wyboru tematu, a nie implementacji.
2. **Szybciej sięgnęlibyśmy po drugie źródło danych**: uchwały powiatów o dyżurach aptek lub geokodowanie adresów z TERYT, żeby uzupełnić braki rejestru.
3. **Ustalilibyśmy procedurę benchmarku wcześniej** (adres, liczba powtórzeń, rozgrzewka), żeby uniknąć mylących pomiarów.
4. **Od pierwszego commita prowadzilibyśmy dokumentację ISO 10013**, a nie uzupełniali ją na końcu.

## Rekomendacje dla kolejnych projektów

| # | Rekomendacja | Dla kogo |
|---|---|---|
| 1 | Przed wyborem zbioru z dane.gov.pl sprawdź go w API: format, aktualność, kompletność kluczowych kolumn | zespoły projektowe |
| 2 | Traktuj ETL jako miejsce na optymalizację: im więcej pracy przy ładowaniu, tym prostsze i szybsze zapytania | programiści |
| 3 | Dane osobowe usuwaj jak najwcześniej w potoku danych i pilnuj tego testem | wszyscy |
| 4 | Utrzymuj małą próbkę prawdziwych danych w testach, żeby CI działało bez dostępu do sieci | programiści |
| 5 | Braki w danych źródłowych komunikuj użytkownikowi wprost i zgłaszaj je dostawcy danych | właściciele produktu |
| 6 | Dla małych zbiorów (do milionów rekordów) wybieraj DuckDB/SQLite zamiast serwera bazy | architekci |

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
