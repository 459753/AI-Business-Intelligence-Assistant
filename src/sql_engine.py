"""Small read-only SQL layer for ad-hoc analysis."""
from __future__ import annotations
import re
import duckdb
import pandas as pd

READ_ONLY = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)


def run_query(frame: pd.DataFrame, query: str) -> pd.DataFrame:
    if not READ_ONLY.match(query) or ";" in query.strip().rstrip(";"):
        raise ValueError("Only one read-only SELECT or WITH query is allowed.")
    connection = duckdb.connect(database=":memory:")
    try:
        connection.register("data", frame)
        return connection.execute(query).fetchdf()
    finally:
        connection.close()
