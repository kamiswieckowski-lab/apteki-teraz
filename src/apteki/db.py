"""Dostęp do danych: DuckDB w pamięci, załadowany z pliku Parquet przy starcie."""

import json
from pathlib import Path

import duckdb

from apteki.hours import DAYS, normalize

RESULT_COLUMNS = [
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
    "wysylkowa",
    "calodobowa",
] + [f"h_{d}" for d in DAYS]


class Store:
    def __init__(self, parquet: Path, meta: Path | None = None):
        if not parquet.exists():
            raise FileNotFoundError(f"Brak pliku {parquet}. Uruchom najpierw: python scripts/fetch_data.py")
        self.con = duckdb.connect(":memory:")
        self.con.execute("CREATE TABLE apteki AS SELECT * FROM read_parquet(?)", [str(parquet)])
        self.meta = json.loads(meta.read_text("utf-8")) if meta and meta.exists() else {}
        # Statystyki nie zmieniają się w trakcie działania - liczymy je raz.
        self.stats = self._compute_stats()
        self.wojewodztwa = sorted(
            (r[0] for r in self._query("SELECT DISTINCT wojewodztwo FROM apteki")), key=normalize
        )
        self.count = self._query("SELECT count(*) FROM apteki")[0][0]

    def _query(self, sql: str, params: list | None = None) -> list[tuple]:
        # Osobny kursor na zapytanie - bezpieczne przy wielu wątkach serwera.
        return self.con.cursor().execute(sql, params or []).fetchall()

    def search(
        self,
        q: str = "",
        wojewodztwo: str = "",
        day: str | None = None,
        minute: int | None = None,
        calodobowa: bool = False,
        wysylkowa: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        where, params = [], []
        for token in normalize(q).split()[:6]:
            where.append("szukaj LIKE ?")
            params.append(f"%{token}%")
        if wojewodztwo:
            where.append("wojewodztwo = ?")
            params.append(wojewodztwo)
        if day in DAYS:
            # nazwy kolumn pochodzą z białej listy DAYS, więc f-string jest bezpieczny
            if minute is None:
                where.append(f"o_{day} IS NOT NULL")
            else:
                where.append(f"o_{day} <= ? AND c_{day} > ?")
                params += [minute, minute]
        if calodobowa:
            where.append("calodobowa")
        if wysylkowa:
            where.append("wysylkowa")
        clause = ("WHERE " + " AND ".join(where)) if where else ""

        total = self._query(f"SELECT count(*) FROM apteki {clause}", params)[0][0]
        rows = self._query(
            f"SELECT {', '.join(RESULT_COLUMNS)} FROM apteki {clause} "
            "ORDER BY miejscowosc, adres LIMIT ? OFFSET ?",
            params + [limit, offset],
        )
        return {"total": total, "items": [dict(zip(RESULT_COLUMNS, r)) for r in rows]}

    def _compute_stats(self) -> dict:
        agg = """
            count(*) AS apteki,
            count(*) FILTER (WHERE calodobowa) AS calodobowe,
            count(*) FILTER (WHERE o_nn IS NOT NULL) AS niedziela,
            count(*) FILTER (WHERE c_pn > 1200) AS po_20
        """
        cols = ["apteki", "calodobowe", "niedziela", "po_20"]
        woj = self._query(f"SELECT wojewodztwo, {agg} FROM apteki GROUP BY 1 ORDER BY 2 DESC")
        bez_calodobowej = self._query(
            f"""SELECT wojewodztwo, powiat, {agg} FROM apteki
                GROUP BY 1, 2 HAVING count(*) FILTER (WHERE calodobowa) = 0
                ORDER BY 3 DESC"""
        )
        total = self._query(f"SELECT {agg} FROM apteki")[0]
        powiaty = self._query("SELECT count(DISTINCT wojewodztwo || powiat) FROM apteki")[0][0]
        return {
            "polska": dict(zip(cols, total)) | {"powiaty": powiaty},
            "wojewodztwa": [{"wojewodztwo": r[0]} | dict(zip(cols, r[1:])) for r in woj],
            "powiaty_bez_calodobowej": [
                {"wojewodztwo": r[0], "powiat": r[1]} | dict(zip(cols, r[2:])) for r in bez_calodobowej
            ],
        }
