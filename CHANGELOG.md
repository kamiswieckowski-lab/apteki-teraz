# Changelog

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-004 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

Format zgodny z [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), wersjonowanie
według [Semantic Versioning](https://semver.org/lang/pl/).

## [Unreleased]

### Dodano

- Publiczne demo na Render: https://apteki-teraz.onrender.com, link w README i raporcie końcowym.

## [1.0.0] - 2026-10-25

### Dodane
- Skrypt `scripts/fetch_data.py` pobierający Rejestr Aptek przez API dane.gov.pl (zbiór 1925).
- ETL: CSV → Parquet, filtrowanie aktywnych aptek publicznych, usuwanie danych osobowych,
  parsowanie godzin otwarcia na minuty, normalizacja tekstu do wyszukiwania.
- Kalendarz: niedziele handlowe (stan prawny od 2025 r.) i święta ustawowe.
- API FastAPI: `/api/search`, `/api/stats`, `/api/meta`, `/health`.
- Frontend: wyszukiwarka z filtrem „otwarta teraz”, dniem i godziną, statystyki i lista powiatów bez apteki całodobowej.
- Testy pytest (37) na zanonimizowanej próbce danych, linter ruff.
- Docker, docker compose, CI w GitHub Actions (lint, testy, build i smoke test obrazu).
- Blueprint `render.yaml` do darmowego wdrożenia na Render.com.
- Dokumentacja: raport końcowy (ISO 21513), lessons learned (PMI), rejestr dokumentów (ISO 10013).
