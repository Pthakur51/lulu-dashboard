import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Data Dashboard")

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("data.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower()



# -------------------------------
# TRY CONVERTING ALL TO NUMERIC WHERE POSSIBLE
# -------------------------------
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
    except:
        pass

# -------------------------------
# FIND NUMERIC COLUMNS AGAIN
# -------------------------------
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

# If still empty → fallback
if not numeric_cols:
    numeric_cols = df.columns.tolist()
    st.warning("⚠ No numeric columns detected. Select manually.")

# -------------------------------
# COLUMN SELECTION
# -------------------------------
st.subheader("🔧 Select Columns")

col1, col2, col3 = st.columns(3)

revenue_col = col1.selectbox("💰 Revenue Column", numeric_cols)
date_col = col2.selectbox("📅 Date/Month Column", df.columns)
product_col = col3.selectbox("📦 Product Column", df.columns)

# Stop if something not selected
if revenue_col is None or date_col is None:
    st.error("❌ Please select valid columns")
    st.stop()

# -------------------------------
# HANDLE DATE
# -------------------------------
try:
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df["month"] = df[date_col].dt.to_period("M").astype(str)
except:
    df["month"] = df[date_col].astype(str)

# -------------------------------
# FILTER
# -------------------------------
st.sidebar.header("Filters")

months = sorted(df["month"].dropna().unique())

if months:
    selected_month = st.sidebar.selectbox("Select Month", months)
    df_filtered = df[df["month"] == selected_month]
else:
    df_filtered = df

# -------------------------------
# SAFE NUMERIC CONVERSION
# -------------------------------
df_filtered[revenue_col] = pd.to_numeric(df_filtered[revenue_col], errors='coerce')

# -------------------------------
# KPI
# -------------------------------
col1, col2 = st.columns(2)

total_revenue = df_filtered[revenue_col].sum()
avg_order = df_filtered[revenue_col].mean()

col1.metric("💰 Total Revenue", f"{total_revenue:,.0f}")
col2.metric("📦 Avg Order", f"{avg_order:,.0f}")

# -------------------------------
# CHARTS
# -------------------------------
tab1, tab2 = st.tabs(["📈 Trend", "📦 Products"])

with tab1:
    trend = df.groupby("month")[revenue_col].sum().reset_index().sort_values("month")
    fig = px.bar(trend, x="month", y=revenue_col)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    prod = df.groupby(product_col)[revenue_col].sum().reset_index()
    fig2 = px.pie(prod, names=product_col, values=revenue_col)
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# DATA VIEW
# -------------------------------
st.subheader("Preview")
st.dataframe(df.head(20))



