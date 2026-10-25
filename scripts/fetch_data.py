"""Pobiera Rejestr Aptek przez API dane.gov.pl i buduje plik Parquet dla aplikacji.

Użycie:
    python scripts/fetch_data.py               # pobierz najnowsze dane
    python scripts/fetch_data.py --if-missing  # tylko gdy brak danych (Docker)
    python scripts/fetch_data.py --sample      # użyj małej próbki z tests/fixtures (offline)
"""

import argparse
import json
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apteki import config, etl  # noqa: E402

SAMPLE = ROOT / "tests" / "fixtures" / "apteki_sample.csv"
USER_AGENT = "apteki-teraz/1.0 (+https://github.com/kamiswieckowski-lab/apteki-teraz)"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def find_resource() -> dict:
    """Szuka w zbiorze zasobu, który wskazuje na generator pliku Rejestru Aptek."""
    url = f"{config.DANE_GOV_API}/datasets/{config.DANE_GOV_DATASET_ID}/resources?per_page=50&sort=-created"
    data = get_json(url)["data"]
    for res in data:
        attrs = res["attributes"]
        link = attrs.get("link") or ""
        if "filegenerator" in link:
            # Generator udostępnia też CSV - jest lżejszy i prostszy niż XLS.
            csv_url = link.rsplit("/", 1)[0] + "/getcsv"
            return {
                "resource_id": res["id"],
                "title": attrs.get("title"),
                "data_date": attrs.get("data_date"),
                "url": csv_url,
            }
    raise RuntimeError("Nie znaleziono zasobu z plikiem Rejestru Aptek w zbiorze dane.gov.pl")


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.replace(dest)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--if-missing", action="store_true", help="nic nie rób, jeśli dane już są")
    parser.add_argument("--sample", action="store_true", help="użyj próbki testowej zamiast pobierania")
    args = parser.parse_args()

    if args.if_missing and config.PARQUET_PATH.exists():
        print(f"Dane już istnieją: {config.PARQUET_PATH}")
        return

    if args.sample:
        src = SAMPLE
        meta = {"zrodlo": "próbka testowa", "data_date": "próbka"}
    else:
        if config.CSV_URL:
            meta = {"url": config.CSV_URL, "data_date": None}
        else:
            print(f"Pytam API dane.gov.pl o zbiór {config.DANE_GOV_DATASET_ID}...")
            meta = find_resource()
        src = config.DATA_DIR / "raw" / "apteki.csv"
        print(f"Pobieram {meta['url']} ...")
        download(meta["url"], src)
        meta["zrodlo"] = f"dane.gov.pl, zbiór {config.DANE_GOV_DATASET_ID} (Rejestr Aptek)"

    count = etl.run(src, config.PARQUET_PATH)
    meta |= {
        "liczba_aptek": count,
        "pobrano": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    if not meta.get("data_date"):
        meta["data_date"] = meta["pobrano"][:10]
    config.META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), "utf-8")
    print(f"Gotowe: {count} aptek -> {config.PARQUET_PATH}")


if __name__ == "__main__":
    main()
