import pandas as pd
import pytest
from src.data_processing import clean_data, outlier_summary
from src.sql_engine import run_query


def test_clean_data_removes_duplicates_and_fills_values():
    raw = pd.DataFrame({"revenue": [10.0, None, 10.0], "region": ["East", None, "East"]})
    result = clean_data(raw)
    assert len(result) == 2
    assert result.isna().sum().sum() == 0


def test_outlier_summary_detects_extreme_value():
    result = outlier_summary(pd.DataFrame({"revenue": [1, 2, 2, 3, 100]}))
    assert result.loc[0, "outlier_count"] == 1


def test_sql_only_accepts_read_queries():
    data = pd.DataFrame({"revenue": [10, 20]})
    assert run_query(data, "SELECT SUM(revenue) AS total FROM data").loc[0, "total"] == 30
    with pytest.raises(ValueError):
        run_query(data, "DROP TABLE data")
