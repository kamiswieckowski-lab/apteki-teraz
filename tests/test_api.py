from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from apteki import api, config


@pytest.fixture(scope="module")
def client(parquet, tmp_path_factory):
    original = config.PARQUET_PATH, config.META_PATH
    config.PARQUET_PATH = parquet
    config.META_PATH = parquet.parent / "brak.json"
    with TestClient(api.app) as c:
        yield c
    config.PARQUET_PATH, config.META_PATH = original


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_meta(client):
    data = client.get("/api/meta").json()
    assert data["liczba_aptek"] == 25
    assert "małopolskie" in data["wojewodztwa"]


def test_search_text_without_polish_chars(client):
    data = client.get("/api/search", params={"q": "krakow"}).json()
    assert data["total"] == 3
    assert all(a["miejscowosc"] == "Kraków" for a in data["items"])


def test_search_pagination(client):
    first = client.get("/api/search", params={"limit": 10}).json()
    second = client.get("/api/search", params={"limit": 10, "offset": 10}).json()
    assert first["total"] == 25
    assert len(first["items"]) == 10
    assert {a["id"] for a in first["items"]}.isdisjoint({a["id"] for a in second["items"]})


def test_search_open_at_night(client):
    data = client.get("/api/search", params={"kiedy": "wt", "godzina": "03:00"}).json()
    assert data["total"] >= 3
    assert all(a["h_wt"].startswith("ca") or a["h_wt"].startswith("00") for a in data["items"])


def test_search_sunday(client):
    data = client.get("/api/search", params={"kiedy": "nn"}).json()
    assert data["total"] == 3
    assert all(a["h_nn"] for a in data["items"])


def test_search_now_uses_clock(client, monkeypatch):
    monkeypatch.setattr(api, "now", lambda: datetime(2026, 10, 25, 3, 0))  # niedziela, noc
    data = client.get("/api/search", params={"kiedy": "teraz"}).json()
    assert data["dzien"] == "nn"
    assert data["minuta"] == 180


def test_filters(client):
    assert client.get("/api/search", params={"calodobowa": True}).json()["total"] == 3
    assert client.get("/api/search", params={"wysylkowa": True}).json()["total"] == 2


def test_invalid_params(client):
    assert client.get("/api/search", params={"kiedy": "xx"}).status_code == 422
    assert client.get("/api/search", params={"limit": 1000}).status_code == 422
    assert client.get("/api/search", params={"kiedy": "pn", "godzina": "abc"}).status_code == 422


def test_stats(client):
    s = client.get("/api/stats").json()
    assert s["polska"]["apteki"] == 25
    assert sum(w["apteki"] for w in s["wojewodztwa"]) == 25
    assert all(p["calodobowe"] == 0 for p in s["powiaty_bez_calodobowej"])


def test_frontend_served_with_cache(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Apteki Teraz" in r.text
    assert "max-age" in r.headers["cache-control"]
