"""Parsowanie godzin otwarcia i kalendarz (niedziele handlowe, święta)."""

import re
from datetime import date, datetime, timedelta

# Klucze dni używane w całej aplikacji. "nh" = niedziela handlowa,
# "nn" = niedziela niehandlowa (oraz święta).
DAYS = ["pn", "wt", "sr", "cz", "pt", "sb", "nh", "nn"]
DAY_LABELS = {
    "pn": "Poniedziałek",
    "wt": "Wtorek",
    "sr": "Środa",
    "cz": "Czwartek",
    "pt": "Piątek",
    "sb": "Sobota",
    "nh": "Niedziela handlowa",
    "nn": "Niedziela niehandlowa / święto",
}
SOURCE_COLUMNS = {
    "pn": "godziny_otwarcia_poniedzialek",
    "wt": "godziny_otwarcia_wtorek",
    "sr": "godziny_otwarcia_sroda",
    "cz": "godziny_otwarcia_czwartek",
    "pt": "godziny_otwarcia_piatek",
    "sb": "godziny_otwarcia_sobota",
    "nh": "godziny_otwarcia_niedziela_handlowa",
    "nn": "godziny_otwarcia_niedziela_niehandlowa",
}

_RANGE_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$")
FULL_DAY = (0, 1440)


def parse_range(text: str | None) -> tuple[int, int] | None:
    """Zamienia np. "08:00 - 16:00" na (480, 960) minut od północy.

    Zwraca None, gdy apteka jest tego dnia zamknięta lub wpis jest nieczytelny.
    Godziny przechodzące przez północ są obcinane do 24:00.
    """
    t = (text or "").strip().strip('"').strip().lower()
    if not t:
        return None
    if t.startswith("całodob") or t.startswith("calodob"):
        return FULL_DAY
    m = _RANGE_RE.match(t)
    if not m:
        return None
    h1, m1, h2, m2 = (int(x) for x in m.groups())
    if h1 > 24 or h2 > 24 or m1 > 59 or m2 > 59:
        return None
    start, end = h1 * 60 + m1, h2 * 60 + m2
    if start >= 1440:
        return None
    if end == 0 or end <= start:
        end = 1440
    return start, min(end, 1440)


def easter(year: int) -> date:
    """Data Wielkanocy (algorytm Meeusa/Jonesa/Butchera)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month = (h + l_ - 7 * m + 114) // 31
    day = (h + l_ - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def public_holidays(year: int) -> set[date]:
    e = easter(year)
    fixed = [(1, 1), (1, 6), (5, 1), (5, 3), (8, 15), (11, 1), (11, 11), (12, 24), (12, 25), (12, 26)]
    days = {date(year, mo, d) for mo, d in fixed}
    days |= {e, e + timedelta(days=1), e + timedelta(days=49), e + timedelta(days=60)}
    return days


def _last_sunday(year: int, month: int) -> date:
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - 6) % 7)


def is_trading_sunday(d: date) -> bool:
    """Niedziele handlowe wg ustawy (stan od 2025 r.)."""
    if d.weekday() != 6:
        return False
    if d in {_last_sunday(d.year, m) for m in (1, 4, 6, 8)}:
        return True
    if d == easter(d.year) - timedelta(days=7):
        return True
    # trzy niedziele przed Wigilią
    return d.month == 12 and 3 <= d.day <= 23


def day_key(d: date) -> str:
    """Który zestaw godzin z rejestru obowiązuje danego dnia."""
    if d in public_holidays(d.year):
        return "nn"
    wd = d.weekday()
    if wd < 6:
        return DAYS[wd]
    return "nh" if is_trading_sunday(d) else "nn"


def minute_of_day(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


_PL = str.maketrans("ąćęłńóśźż", "acelnoszz")


def normalize(text: str) -> str:
    """Tekst do wyszukiwania: małe litery, bez polskich znaków."""
    return " ".join(text.lower().translate(_PL).split())
