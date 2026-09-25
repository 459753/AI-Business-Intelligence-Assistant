"""Dataset ingestion, cleaning, and interpretable profiling."""
from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class DataProfile:
    rows: int
    columns: int
    duplicates: int
    missing_cells: int
    numeric_columns: list[str]
    datetime_columns: list[str]


def infer_dates(frame: pd.DataFrame, threshold: float = 0.75) -> pd.DataFrame:
    """Parse likely date columns without coercing ordinary numeric fields."""
    result = frame.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        if any(token in column.lower() for token in ("date", "time", "month", "year")):
            parsed = pd.to_datetime(result[column], errors="coerce")
            if parsed.notna().mean() >= threshold:
                result[column] = parsed
    return result


def clean_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply predictable defaults: median for numeric, mode/Unknown for labels."""
    result = infer_dates(frame)
    result = result.drop_duplicates().copy()
    for column in result.columns:
        if pd.api.types.is_numeric_dtype(result[column]):
            result[column] = result[column].fillna(result[column].median())
        elif pd.api.types.is_datetime64_any_dtype(result[column]):
            continue
        else:
            mode = result[column].mode(dropna=True)
            result[column] = result[column].fillna(mode.iloc[0] if not mode.empty else "Unknown")
    return result


def profile_data(frame: pd.DataFrame) -> DataProfile:
    return DataProfile(
        rows=len(frame), columns=len(frame.columns), duplicates=int(frame.duplicated().sum()),
        missing_cells=int(frame.isna().sum().sum()),
        numeric_columns=frame.select_dtypes(include="number").columns.tolist(),
        datetime_columns=frame.select_dtypes(include="datetime").columns.tolist(),
    )


def outlier_summary(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for column in frame.select_dtypes(include="number"):
        series = frame[column].dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        records.append({"column": column, "lower_bound": lower, "upper_bound": upper,
                        "outlier_count": int(((series < lower) | (series > upper)).sum())})
    return pd.DataFrame(records)


def add_date_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result.select_dtypes(include="datetime").columns:
        result[f"{column}_year"] = result[column].dt.year
        result[f"{column}_month"] = result[column].dt.month
        result[f"{column}_quarter"] = result[column].dt.quarter
    return result
