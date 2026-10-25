import duckdb

from apteki import etl

from .conftest import FIXTURE


def test_only_active_public_pharmacies(parquet):
    con = duckdb.connect()
    total = con.execute("SELECT count(*) FROM read_parquet(?)", [str(parquet)]).fetchone()[0]
    expected = sum(1 for _ in etl.read_rows(FIXTURE))
    assert total == expected == 25
    kinds = {
        r[0] for r in con.execute("SELECT DISTINCT rodzaj FROM read_parquet(?)", [str(parquet)]).fetchall()
    }
    assert kinds <= {"apteka ogólnodostępna", "punkt apteczny"}


def test_no_personal_data_columns(parquet):
    con = duckdb.connect()
    cols = [r[0] for r in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(parquet)]).fetchall()]
    assert cols == etl.COLUMNS
    assert not any(c.startswith(("kierownik", "zastepca", "wlasciciel")) for c in cols)


def test_transform_row_skips_inactive():
    assert etl.transform_row({"stan_apteki": "NIEAKTYWNA", "rodzaj_apteki": "PUNKT APTECZNY"}) is None


def test_transform_row_values():
    row = {
        "identyfikator_apteki": "1",
        "nazwa_apteki": "",
        "stan_apteki": "AKTYWNA",
        "rodzaj_apteki": "APTEKA OGÓLNODOSTĘPNA",
        "wojewodztwo": "KUJAWSKO POMORSKIE",
        "miejscowosc": "TORUŃ",
        "typ_ulicy": "ul.",
        "nazwa_ulicy": "Szeroka",
        "numer_budynku": "1",
        "numer_lokalu": "2",
        "wlasciciel_nazwa": "Jan Kowalski",
        "wlasciciel_forma_prawna": "Osoba fizyczna prowadząca działalność gospodarczą",
        "godziny_otwarcia_poniedzialek": "całodobowo",
        "godziny_otwarcia_niedziela_niehandlowa": "10:00 - 14:00",
        "czy_szprzedaz_wysylkowa": "TAK",
    }
    out = etl.transform_row(row)
    assert out["nazwa"] == "Apteka ogólnodostępna"  # nie ujawniamy nazwiska osoby fizycznej
    assert out["wojewodztwo"] == "kujawsko-pomorskie"
    assert out["miejscowosc"] == "Toruń"
    assert out["adres"] == "ul. Szeroka 1/2"
    assert (out["o_pn"], out["c_pn"]) == (0, 1440)
    assert (out["o_nh"], out["c_nh"]) == (600, 840)  # niedziela handlowa uzupełniona
    assert out["wysylkowa"] is True
    assert out["calodobowa"] is False  # wtorek-sobota zamknięte
    assert "torun" in out["szukaj"]
