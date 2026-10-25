# Jak współtworzyć Apteki Teraz

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-002 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

Dziękujemy za chęć pomocy! Każdy wkład się liczy, także zgłoszenie literówki.

## Zgłaszanie błędów

1. Sprawdź w [Issues](https://github.com/kamiswieckowski-lab/apteki-teraz/issues), czy błąd nie został już zgłoszony.
2. Załóż nowe zgłoszenie z szablonu **Zgłoszenie błędu** i opisz, jak odtworzyć problem.
3. **Błędne godziny lub adres apteki** to zwykle błąd w źródłowym Rejestrze Aptek, a nie w aplikacji.
   Zgłoś go z identyfikatorem apteki, a my przekażemy informację dalej lub dodamy wyjątek w ETL.

Pomysły na nowe funkcje zgłaszaj z szablonu **Propozycja funkcji**.

## Zmiany w kodzie

1. Zrób fork i utwórz gałąź od `main`: `git checkout -b fix/krotki-opis`.
2. Przygotuj środowisko:
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt
   python scripts/fetch_data.py --sample
   ```
3. Wprowadź zmiany i dopisz testy w `tests/`.
4. Upewnij się, że wszystko przechodzi:
   ```bash
   ruff check . && ruff format --check . && pytest
   ```
5. Dopisz zmianę do sekcji *Unreleased* w `CHANGELOG.md`.
6. Otwórz pull request. Szablon PR zawiera checklistę, a CI uruchomi linter, testy i build obrazu Dockera.

## Zasady

- Styl kodu wyznacza `ruff` (konfiguracja w `pyproject.toml`).
- Komunikaty commitów piszemy w trybie rozkazującym, np. „Dodaj filtr aptek całodobowych”.
- **Nie dodawaj do repozytorium danych** (`data/` jest w `.gitignore`) ani **sekretów**: konfiguracja trafia do zmiennych środowiskowych (`.env.example`).
- **Nie przetwarzaj danych osobowych.** ETL celowo usuwa dane kierowników i właścicieli aptek.
- Zmieniając dokument w `docs/`, podbij jego wersję i dopisz wiersz w historii zmian (ISO 10013).

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
