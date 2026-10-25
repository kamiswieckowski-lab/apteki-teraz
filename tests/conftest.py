from pathlib import Path

import pytest

from apteki import etl

FIXTURE = Path(__file__).parent / "fixtures" / "apteki_sample.csv"


@pytest.fixture(scope="session")
def parquet(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("data") / "apteki.parquet"
    etl.run(FIXTURE, out)
    return out
