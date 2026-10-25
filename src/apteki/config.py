"""Konfiguracja aplikacji - wyłącznie ze zmiennych środowiskowych."""

import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
PARQUET_PATH = DATA_DIR / "apteki.parquet"
META_PATH = DATA_DIR / "meta.json"

DANE_GOV_API = os.getenv("DANE_GOV_API", "https://api.dane.gov.pl/1.4")
DANE_GOV_DATASET_ID = os.getenv("DANE_GOV_DATASET_ID", "1925")
# Opcjonalne nadpisanie adresu pliku CSV (np. lokalny mirror).
CSV_URL = os.getenv("CSV_URL", "")

TIMEZONE = os.getenv("TZ_NAME", "Europe/Warsaw")
MAX_PAGE_SIZE = 100
