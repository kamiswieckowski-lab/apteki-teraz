"""API HTTP (FastAPI) + serwowanie statycznego frontendu."""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from apteki import __version__, config
from apteki.db import Store
from apteki.hours import DAY_LABELS, DAYS, day_key, minute_of_day

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = Store(config.PARQUET_PATH, config.META_PATH)
    yield


app = FastAPI(title="Apteki Teraz", version=__version__, lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api/stats") or path.startswith("/api/meta"):
        response.headers["Cache-Control"] = "public, max-age=3600"
    elif not path.startswith("/api") and response.status_code == 200:
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response


def now() -> datetime:
    return datetime.now(ZoneInfo(config.TIMEZONE))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta(request: Request):
    store: Store = request.app.state.store
    return {
        "wersja": __version__,
        "liczba_aptek": store.count,
        "wojewodztwa": store.wojewodztwa,
        "dni": DAY_LABELS,
        "zrodlo": store.meta,
    }


@app.get("/api/stats")
def stats(request: Request):
    return request.app.state.store.stats


@app.get("/api/search")
def search(
    request: Request,
    response: Response,
    q: str = Query("", max_length=100),
    wojewodztwo: str = "",
    kiedy: str = Query("", description="'teraz', klucz dnia (pn..nn) albo puste"),
    godzina: str = Query("", pattern=r"^(\d{1,2}:\d{2})?$"),
    calodobowa: bool = False,
    wysylkowa: bool = False,
    limit: int = Query(20, ge=1, le=config.MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
):
    day, minute = None, None
    if kiedy == "teraz":
        t = now()
        day, minute = day_key(t.date()), minute_of_day(t)
    elif kiedy:
        if kiedy not in DAYS:
            raise HTTPException(422, "Nieznany dzień")
        day = kiedy
        if godzina:
            h, m = (int(x) for x in godzina.split(":"))
            minute = h * 60 + m
    store: Store = request.app.state.store
    result = store.search(q, wojewodztwo, day, minute, calodobowa, wysylkowa, limit, offset)
    result["dzien"] = day
    result["minuta"] = minute
    result["dzisiaj"] = day_key(now().date())
    response.headers["Cache-Control"] = "no-store" if kiedy == "teraz" else "public, max-age=300"
    return result


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
