# AI Business Intelligence Assistant

An original, portfolio-ready Streamlit application that turns a CSV into a business analysis workspace: data quality checks, outlier review, feature engineering, interactive KPI exploration, SQL queries, and optional LLM-backed recommendations.

## Highlights

- Upload any CSV and receive a reusable data-quality report.
- Clean missing values with transparent, conservative defaults.
- Identify numeric outliers with an IQR method.
- Derive date-based features for time-series analysis.
- Explore KPIs, trends, category performance, and distributions with Plotly.
- Query the current dataset with read-only SQL through DuckDB.
- Generate decision-focused recommendations with OpenAI when an API key is configured; a local insight fallback keeps the app useful without one.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL, upload a CSV, and choose a page in the sidebar. Use `data/sample_sales.csv` to explore immediately.

## Optional OpenAI setup

Create `.streamlit/secrets.toml` (never commit it):

```toml
OPENAI_API_KEY = "your_key_here"
```

The assistant sends only the dataset profile and calculated KPI summary—not the full CSV—to the model. It also works without a key by returning deterministic, data-based insights.

## Recommended CSV fields

The app accepts flexible column names. For the richest dashboard, include a numeric measure such as `revenue` or `sales`, a date, and a category or region. Example fields: `order_date`, `region`, `category`, `revenue`, `profit`, `quantity`.

## Project structure

```text
app.py                 Streamlit UI and workflow
src/data_processing.py Cleaning, profiling, outlier detection, features
src/analytics.py       KPIs and Plotly figures
src/sql_engine.py      Read-only DuckDB query layer
src/recommendations.py LLM and local recommendation service
tests/                 Unit tests for core analysis behavior
```

## Run checks

```bash
pytest -q
```

## Design notes

SQL is limited to a single read-only `SELECT`/`WITH` statement against the `data` table. The code deliberately separates ingestion, analysis, querying, and recommendations so those layers can be replaced or scaled independently.
