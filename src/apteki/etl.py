"""ETL: surowy CSV z Rejestru Aptek -> oczyszczony plik Parquet.

- zostawiamy tylko aktywne apteki dostępne dla pacjentów (bez szpitalnych),
- usuwamy dane osobowe (kierownicy, imiona i nazwiska właścicieli),
- godziny otwarcia zamieniamy na minuty od północy, żeby filtrować liczbami,
- przygotowujemy znormalizowaną kolumnę do wyszukiwania pełnotekstowego.
"""

import csv
import sys
import tempfile
from pathlib import Path

import duckdb

from apteki.hours import DAYS, FULL_DAY, SOURCE_COLUMNS, normalize, parse_range

PUBLIC_TYPES = {"APTEKA OGÓLNODOSTĘPNA", "PUNKT APTECZNY"}

TEXT_COLUMNS = [
    "id",
    "nazwa",
    "rodzaj",
    "wojewodztwo",
    "powiat",
    "gmina",
    "miejscowosc",
    "adres",
    "kod_pocztowy",
    "telefon",
    "email",
    "www",
    "szukaj",
]
BOOL_COLUMNS = ["wysylkowa", "calodobowa"]
HOUR_COLUMNS = [f"{p}_{d}" for d in DAYS for p in ("o", "c")]
RAW_HOUR_COLUMNS = [f"h_{d}" for d in DAYS]
COLUMNS = TEXT_COLUMNS + BOOL_COLUMNS + HOUR_COLUMNS + RAW_HOUR_COLUMNS


def _clean(value: str | None) -> str:
    v = (value or "").strip()
    return "" if v == '""' else v


def _place(value: str) -> str:
    return value.title() if value.isupper() else value


def _name(row: dict) -> str:
    name = _clean(row.get("nazwa_apteki"))
    if name:
        return name
    # Nazwa właściciela tylko dla firm - nie dla osób fizycznych (RODO).
    owner = _clean(row.get("wlasciciel_nazwa"))
    if owner and "osoba fizyczna" not in _clean(row.get("wlasciciel_forma_prawna")).lower():
        return owner
    return _clean(row.get("rodzaj_apteki")).capitalize() or "Apteka"


def _address(row: dict) -> str:
    street = " ".join(x for x in (_clean(row.get("typ_ulicy")), _clean(row.get("nazwa_ulicy"))) if x)
    number = _clean(row.get("numer_budynku"))
    flat = _clean(row.get("numer_lokalu"))
    if flat:
        number = f"{number}/{flat}"
    if not street:
        street = _place(_clean(row.get("miejscowosc")))
    return " ".join(f"{street} {number}".split())


def transform_row(row: dict) -> dict | None:
    """Zwraca oczyszczony rekord albo None, gdy apteka nie jest publiczna/aktywna."""
    if _clean(row.get("stan_apteki")) != "AKTYWNA":
        return None
    if _clean(row.get("rodzaj_apteki")).upper() not in PUBLIC_TYPES:
        return None

    out = {
        "id": _clean(row.get("identyfikator_apteki")),
        "nazwa": _name(row),
        "rodzaj": _clean(row.get("rodzaj_apteki")).lower(),
        "wojewodztwo": _clean(row.get("wojewodztwo")).lower().replace(" ", "-"),
        "powiat": _clean(row.get("powiat")).lower(),
        "gmina": _place(_clean(row.get("gmina"))),
        "miejscowosc": _place(_clean(row.get("miejscowosc"))),
        "adres": _address(row),
        "kod_pocztowy": _clean(row.get("kod_pocztowy")),
        "telefon": _clean(row.get("telefon")),
        "email": _clean(row.get("email")),
        "www": _clean(row.get("adres_www")),
        "wysylkowa": _clean(row.get("czy_szprzedaz_wysylkowa")).upper() == "TAK",
    }
    out["szukaj"] = normalize(
        " ".join(out[k] for k in ("nazwa", "miejscowosc", "adres", "kod_pocztowy", "gmina", "powiat"))
    )
    ranges = {}
    for d in DAYS:
        raw = _clean(row.get(SOURCE_COLUMNS[d]))
        if d == "nh" and not raw:
            # W rejestrze kolumna "niedziela handlowa" bywa pusta - wtedy
            # przyjmujemy godziny niedzielne podane dla niedzieli niehandlowej.
            raw = _clean(row.get(SOURCE_COLUMNS["nn"]))
        rng = parse_range(raw)
        ranges[d] = rng
        out[f"o_{d}"], out[f"c_{d}"] = rng if rng else (None, None)
        out[f"h_{d}"] = raw
    out["calodobowa"] = all(ranges[d] == FULL_DAY for d in ("pn", "wt", "sr", "cz", "pt", "sb"))
    return out


def read_rows(src: Path):
    with open(src, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="|"):
            cleaned = transform_row(row)
            if cleaned:
                yield cleaned


def run(src: Path, out: Path) -> int:
    """Przetwarza CSV do Parquet. Zwraca liczbę zapisanych aptek."""
    out.parent.mkdir(parents=True, exist_ok=True)
    kinds = {c: "BOOLEAN" for c in BOOL_COLUMNS} | {c: "SMALLINT" for c in HOUR_COLUMNS}
    types = {c: kinds.get(c, "VARCHAR") for c in COLUMNS}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_csv = Path(tmp) / "clean.csv"
        count = 0
        with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            for row in read_rows(src):
                writer.writerow(row)
                count += 1

        con = duckdb.connect()
        con.execute(
            f"""
            COPY (
                SELECT * FROM read_csv(?, header = true, columns = {types!r})
                ORDER BY wojewodztwo, miejscowosc, adres
            ) TO '{out.as_posix()}' (FORMAT parquet, COMPRESSION zstd)
            """,
            [str(tmp_csv)],
        )
        con.close()
    return count


if __name__ == "__main__":
    n = run(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Zapisano {n} aptek")
