from __future__ import annotations
import pandas as pd
import streamlit as st

from src.analytics import category_chart, kpis, trend_chart
from src.data_processing import add_date_features, clean_data, outlier_summary, profile_data
from src.recommendations import generate_recommendation
from src.sql_engine import run_query

st.set_page_config(page_title="AI BI Assistant", page_icon="📊", layout="wide")
st.title("AI Business Intelligence Assistant")
st.caption("Upload a CSV to clean, explore, query, and turn data into business actions.")

upload = st.sidebar.file_uploader("Upload CSV", type="csv")
if upload is None:
    st.info("Upload a CSV or use the included sample file by running the app locally.")
    st.stop()

try:
    raw = pd.read_csv(upload)
except Exception as error:
    st.error(f"Could not read that CSV: {error}")
    st.stop()

clean = add_date_features(clean_data(raw))
profile = profile_data(raw)
numeric = clean.select_dtypes(include="number").columns.tolist()
if not numeric:
    st.warning("This CSV has no numeric columns to analyze.")
    st.dataframe(clean.head(100))
    st.stop()

measure = st.sidebar.selectbox("KPI measure", numeric)
categorical = clean.select_dtypes(include=["object", "category"]).columns.tolist()
date_columns = clean.select_dtypes(include="datetime").columns.tolist()
page = st.sidebar.radio("Workspace", ["Overview", "Dashboard", "Data quality", "SQL explorer", "AI recommendations"])

if page == "Overview":
    metrics = kpis(clean, measure)
    columns = st.columns(4)
    for container, (label, value) in zip(columns, metrics.items()):
        container.metric(label.replace("_", " ").title(), f"{value:,.2f}" if label != "records" else f"{value:,}")
    st.subheader("Prepared data")
    st.dataframe(clean.head(100), use_container_width=True)

elif page == "Dashboard":
    if date_columns:
        st.plotly_chart(trend_chart(clean, date_columns[0], measure), use_container_width=True)
    if categorical:
        category = st.selectbox("Dimension", categorical)
        st.plotly_chart(category_chart(clean, category, measure), use_container_width=True)
    else:
        st.info("Add a text category column to compare groups.")

elif page == "Data quality":
    st.write(f"Raw input: **{profile.rows:,} rows**, **{profile.columns} columns**, **{profile.duplicates:,} duplicate rows**, and **{profile.missing_cells:,} missing cells**.")
    st.caption("The prepared dataset removes duplicates, fills numeric gaps with medians, fills labels with their mode, and adds date features.")
    st.subheader("IQR outlier review")
    st.dataframe(outlier_summary(clean), use_container_width=True)

elif page == "SQL explorer":
    st.caption("The prepared dataset is available as the table `data`. Only one SELECT or WITH query is accepted.")
    query = st.text_area("SQL", "SELECT * FROM data LIMIT 20", height=120)
    if st.button("Run query"):
        try:
            st.dataframe(run_query(clean, query), use_container_width=True)
        except Exception as error:
            st.error(str(error))

else:
    category = st.selectbox("Optional comparison dimension", ["None", *categorical])
    if st.button("Generate recommendations"):
        key = st.secrets.get("OPENAI_API_KEY", None)
        with st.spinner("Analyzing your KPI summary..."):
            try:
                st.markdown(generate_recommendation(clean, measure, None if category == "None" else category, key))
            except Exception as error:
                st.error(f"Recommendation service unavailable: {error}")
