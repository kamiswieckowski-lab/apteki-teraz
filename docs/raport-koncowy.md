# Raport końcowy projektu

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-014 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

Struktura raportu opiera się na wytycznych zamknięcia projektu z normy **ISO 21513**
(cel, rezultaty, porównanie z planem, wpływ, wnioski).

## 1. Informacje o projekcie

| | |
|---|---|
| Nazwa | Apteki Teraz |
| Repozytorium | <https://github.com/kamiswieckowski-lab/apteki-teraz> |
| Demo | <https://apteki-teraz.onrender.com> |
| Kierownik / wykonawca | Kamil Wieckowski |
| Okres realizacji | 1 tydzień (zakończenie 2026-10-25) |
| Plan bazowy | [APT-DOC-011 Plan projektu](plan-projektu.md) |

## 2. Cel projektu

**Problem:** osoba szukająca leków w nocy, w niedzielę lub w święto nie ma prostego, ogólnopolskiego
narzędzia opartego na oficjalnych danych. Rejestr Aptek ma godziny otwarcia, ale publikuje je jako
duży plik tabelaryczny.

**Cel:** udostępnić te dane w postaci szybkiej, darmowej, otwartoźródłowej wyszukiwarki oraz pokazać
skalę problemu (gdzie brakuje aptek całodobowych).

## 3. Rezultaty

| Produkt | Stan | Gdzie |
|---|---|---|
| Skrypt pobierający dane z API dane.gov.pl | dostarczony | `scripts/fetch_data.py` |
| ETL z anonimizacją i parsowaniem godzin | dostarczony | `src/apteki/etl.py`, `hours.py` |
| API wyszukiwania i statystyk | dostarczone | `src/apteki/api.py`, `db.py` |
| Interfejs WWW | dostarczony | `src/apteki/static/` |
| Testy automatyczne (37) i linter | dostarczone | `tests/`, `pyproject.toml` |
| CI: lint, testy, build i smoke test Dockera | dostarczone | `.github/workflows/ci.yml` |
| Uruchomienie jedną komendą | dostarczone | `docker compose up` |
| Publiczne demo | wdrożone | <https://apteki-teraz.onrender.com> (Render, plan Free) |
| Dokumentacja (ISO 10013, ISO 21513, PMI) | dostarczona | `docs/` |

### Kluczowe liczby

- **12 052** aktywne apteki i punkty apteczne w wyszukiwarce,
- wyszukiwanie: **16–26 ms** (mediana), odpowiedź ok. **2 kB** po kompresji,
- frontend: ok. **13 kB** bez zewnętrznych zależności,
- pełne odświeżenie danych: ok. **2,5 s**,
- **286 z 381** powiatów nie ma według rejestru ani jednej apteki całodobowej,
- tylko **2%** aptek podaje w rejestrze godziny niedzielne.

## 4. Porównanie z planem

### Zakres

| Planowane | Zrealizowane | Komentarz |
|---|---|---|
| Wyszukiwarka z filtrem „otwarta teraz” | ✅ | dodatkowo obsługa świąt i niedziel handlowych |
| Filtr dzień + godzina | ✅ | |
| Statystyki per województwo i powiat | ✅ | dodatkowo ranking „białych plam” |
| Uruchomienie jedną komendą | ✅ | + alternatywa bez Dockera |
| CI | ✅ | + smoke test obrazu Dockera |
| Mapa | ❌ (poza zakresem) | rejestr nie zawiera współrzędnych, zastąpiona linkiem do map |

### Harmonogram

| Kamień milowy | Plan | Wykonanie | Odchylenie |
|---|---|---|---|
| M1 Wybór danych | dzień 1 | dzień 1 | brak. Odrzucono 2 inne tematy (rejestr żłobków, ceny mieszkań deweloperów) |
| M2 Pipeline danych | dzień 2 | dzień 2 | brak |
| M3 API + frontend | dzień 3–4 | dzień 3 | szybciej dzięki prostemu stackowi |
| M4 Jakość / CI | dzień 5 | dzień 4–5 | brak |
| M5 Wdrożenie + dokumentacja | dzień 6 | dzień 6 | brak |
| M6 Demo | dzień 7 | dzień 7 | brak |

### Założenia wydajnościowe

| Założenie | Cel | Wynik |
|---|---|---|
| Odpowiedź API (mediana) | < 100 ms | 13–26 ms ✅ |
| Rozmiar strony | < 50 kB | ok. 13 kB ✅ |
| Odświeżenie danych | < 1 min | ok. 2,5 s ✅ |

### Koszty

Projekt nie poniósł kosztów: narzędzia open source, darmowe CI (GitHub Actions) i darmowy hosting (Render, plan Free).

## 5. Wpływ

- **Dla mieszkańców:** szybka odpowiedź na pytanie „gdzie kupię lek teraz?”, także na telefonie, bez reklam i rejestracji.
- **Dla samorządów i dziennikarzy:** ranking powiatów bez aptek całodobowych to argument w dyskusji o dyżurach aptek.
- **Dla dostawcy danych:** udokumentowane braki jakości (pusta kolumna „niedziela handlowa”, 2% wypełnienia godzin niedzielnych, niespójne nazwy województw) mogą pomóc Ministerstwu Zdrowia poprawić rejestr.
- **Dla społeczności open source:** odtwarzalny pipeline (jedna komenda) można przenieść na inne rejestry medyczne.

## 6. Wnioski

1. Dane publiczne są „otwarte” formalnie, ale bez przetworzenia trudno z nich skorzystać. Największą wartość dało przygotowanie danych (ETL), a nie samo UI.
2. Jakość danych ogranicza użyteczność: najważniejsza funkcja („apteka w niedzielę”) zależy od pola wypełnionego przez 2% aptek. Trzeba to jasno komunikować użytkownikowi.
3. Prosty stack (DuckDB + FastAPI + czysty JS) wystarczył z dużym zapasem wydajności.
4. Rekomendacje dalszego rozwoju: import uchwał powiatów o dyżurach aptek, geokodowanie adresów (np. TERYT/PRG) i mapa, PWA do użytku offline, codzienne odświeżanie danych (GitHub Actions + cron).

Szczegółowe wnioski procesowe opisuje [APT-DOC-015 Lessons learned](lessons-learned.md).

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
