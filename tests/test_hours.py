from datetime import date, datetime

import pytest

from apteki.hours import day_key, easter, is_trading_sunday, minute_of_day, normalize, parse_range


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("08:00 - 16:00", (480, 960)),
        ("8:30 - 20:00", (510, 1200)),
        ("00:00 - 24:00", (0, 1440)),
        ("całodobowo", (0, 1440)),
        ("20:00 - 02:00", (1200, 1440)),  # przez północ - obcięte do 24:00
        ("08:00 - 00:00", (480, 1440)),
        ("", None),
        ('""', None),
        (None, None),
        ("08:00 - ", None),
        ("08:00 - 16;0", None),
        ("25:00 - 26:00", None),
    ],
)
def test_parse_range(text, expected):
    assert parse_range(text) == expected


def test_easter():
    assert easter(2026) == date(2026, 4, 5)
    assert easter(2027) == date(2027, 3, 28)


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        (date(2026, 1, 25), True),  # ostatnia niedziela stycznia
        (date(2026, 3, 29), True),  # niedziela przed Wielkanocą
        (date(2026, 12, 6), True),  # niedziele przed Wigilią
        (date(2026, 12, 20), True),
        (date(2026, 10, 25), False),
        (date(2026, 10, 26), False),  # poniedziałek
    ],
)
def test_trading_sunday(d, expected):
    assert is_trading_sunday(d) is expected


def test_day_key():
    assert day_key(date(2026, 10, 26)) == "pn"
    assert day_key(date(2026, 10, 31)) == "sb"
    assert day_key(date(2026, 10, 25)) == "nn"
    assert day_key(date(2026, 1, 25)) == "nh"
    assert day_key(date(2026, 11, 11)) == "nn"  # święto w środę


def test_minute_of_day():
    assert minute_of_day(datetime(2026, 1, 1, 21, 15)) == 1275


def test_normalize():
    assert normalize("  Łódź  ŻÓŁTA  ") == "lodz zolta"
