"""Business metrics and interactive chart builders."""
from __future__ import annotations
import pandas as pd
import plotly.express as px


def kpis(frame: pd.DataFrame, measure: str) -> dict[str, float]:
    values = pd.to_numeric(frame[measure], errors="coerce").dropna()
    return {"total": float(values.sum()), "average": float(values.mean()), "median": float(values.median()), "records": int(len(frame))}


def trend_chart(frame: pd.DataFrame, date_column: str, measure: str):
    chart_data = frame.dropna(subset=[date_column]).groupby(date_column, as_index=False)[measure].sum().sort_values(date_column)
    return px.line(chart_data, x=date_column, y=measure, markers=True, title=f"{measure.title()} over time")


def category_chart(frame: pd.DataFrame, category: str, measure: str):
    chart_data = frame.groupby(category, as_index=False)[measure].sum().sort_values(measure, ascending=False).head(20)
    return px.bar(chart_data, x=category, y=measure, color=measure, title=f"{measure.title()} by {category.title()}")
