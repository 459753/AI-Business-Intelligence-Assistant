"""Grounded business recommendations with an optional OpenAI provider."""
from __future__ import annotations
import json
import os
import pandas as pd


def local_insights(frame: pd.DataFrame, measure: str, category: str | None) -> str:
    total = frame[measure].sum()
    message = [f"The dataset contains {len(frame):,} records and {measure} totals {total:,.2f}."]
    if category:
        grouped = frame.groupby(category)[measure].sum().sort_values(ascending=False)
        if len(grouped):
            message.append(f"Prioritize {grouped.index[0]}: it contributes {grouped.iloc[0] / total:.1%} of {measure}.")
            if len(grouped) > 1:
                message.append(f"Investigate {grouped.index[-1]}, the lowest-contributing {category}.")
    return "\n\n".join(message)


def generate_recommendation(frame: pd.DataFrame, measure: str, category: str | None, api_key: str | None = None) -> str:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return local_insights(frame, measure, category)
    summary = {"records": len(frame), "measure": measure, "total": float(frame[measure].sum()), "mean": float(frame[measure].mean())}
    if category:
        summary["top_categories"] = frame.groupby(category)[measure].sum().sort_values(ascending=False).head(5).to_dict()
    from openai import OpenAI
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a concise business analyst. Use only the supplied metrics. Give 3 prioritized, actionable recommendations and mention uncertainty."},
                  {"role": "user", "content": json.dumps(summary)}], temperature=0.2)
    return response.choices[0].message.content or "No recommendation returned."
