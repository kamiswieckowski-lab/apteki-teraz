"""Prosty pomiar czasu odpowiedzi API (uruchom przy działającym serwerze).

python scripts/benchmark.py [http://127.0.0.1:8000] [liczba_powtórzeń]
"""

import statistics
import sys
import time
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 50

CASES = {
    "strona główna (/)": "/",
    "wszystkie apteki, 1. strona": "/api/search",
    "otwarte teraz": "/api/search?kiedy=teraz",
    "tekst: 'warszawa marszalkowska'": "/api/search?q=warszawa%20marszalkowska",
    "wtorek 23:30, mazowieckie": "/api/search?kiedy=wt&godzina=23:30&wojewodztwo=mazowieckie",
    "statystyki": "/api/stats",
}


def measure(path: str) -> tuple[float, float, int]:
    times, size = [], 0
    for _ in range(N):
        req = urllib.request.Request(BASE + path, headers={"Accept-Encoding": "gzip"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req) as r:
            size = len(r.read())
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    return statistics.median(times), times[int(len(times) * 0.95) - 1], size


print(f"{'zapytanie':40} {'mediana':>9} {'p95':>9} {'rozmiar':>9}")
for name, path in CASES.items():
    med, p95, size = measure(path)
    print(f"{name:40} {med:7.1f}ms {p95:7.1f}ms {size / 1024:7.1f}kB")
