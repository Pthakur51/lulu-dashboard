import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("data.csv")
df['order_datetime'] = pd.to_datetime(df['order_datetime'])

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("🔎 Filters")
st.sidebar.markdown("All charts update instantly.")

# Date Range
date_range = st.sidebar.date_input(
    "Date Range",
    [df['order_datetime'].min(), df['order_datetime'].max()]
)

# City
cities = st.sidebar.multiselect(
    "City",
    df['city'].dropna().unique(),
    default=df['city'].dropna().unique()
)

# Channel
channels = st.sidebar.multiselect(
    "Channel",
    df['channel'].dropna().unique(),
    default=df['channel'].dropna().unique()
)

# Department
departments = st.sidebar.multiselect(
    "Department",
    df['department'].dropna().unique(),
    default=df['department'].dropna().unique()
)

# Gender ✅
genders = st.sidebar.multiselect(
    "Gender",
    df['gender'].dropna().unique(),
    default=df['gender'].dropna().unique()
)

# Campaign ✅
campaigns = st.sidebar.multiselect(
    "Campaign",
    df['campaign'].dropna().unique(),
    default=df['campaign'].dropna().unique()
)

# Age Range ✅
age_min = int(df['age'].min())
age_max = int(df['age'].max())

age_range = st.sidebar.slider(
    "Customer Age Range",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max)
)

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered_df = df[
    (df['order_datetime'].dt.date >= date_range[0]) &
    (df['order_datetime'].dt.date <= date_range[1]) &
    (df['city'].isin(cities)) &
    (df['channel'].isin(channels)) &
    (df['department'].isin(departments)) &
    (df['gender'].isin(genders)) &
    (df['campaign'].isin(campaigns)) &
    (df['age'] >= age_range[0]) &
    (df['age'] <= age_range[1])
]

# -----------------------------
# KPIs
# -----------------------------
total_revenue = filtered_df['line_value_aed'].sum()
total_qty = filtered_df['quantity'].sum()
avg_order_value = total_revenue / filtered_df['order_id'].nunique()
return_rate = filtered_df['returned'].mean() * 100

# -----------------------------
# TITLE
# -----------------------------
st.title("🛒 Retail Analytics Dashboard | Lulu UAE Sales Analysis")
st.markdown(f"**{len(filtered_df):,} transactions shown**")

# -----------------------------
# TABS
# -----------------------------
tabs = st.tabs([
    "📊 Overview",
    "📈 Trend Analysis",
    "📦 Category Analysis",
    "⚖️ Comparison",
    "📋 Data Table"
])

# -----------------------------
# TAB 1 — OVERVIEW
# -----------------------------
with tabs[0]:

    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns([3,2,2,2])

    col1.metric("Total Revenue", f"AED {total_revenue:,.0f}")
    col2.metric("Total Quantity", f"{total_qty:,}")
    col3.metric("Avg Order Value", f"AED {avg_order_value:,.1f}")
    col4.metric("Return Rate", f"{return_rate:.2f}%")

    col1, col2 = st.columns(2)

    # Revenue by City
    city_rev = filtered_df.groupby('city')['line_value_aed'].sum().reset_index()
    fig1 = px.pie(
        city_rev,
        names='city',
        values='line_value_aed',
        hole=0.4,
        title="Revenue by City"
    )
    col1.plotly_chart(fig1, use_container_width=True)

    # Payment Method
    pay = filtered_df.groupby('payment_method')['quantity'].sum().reset_index()
    fig2 = px.pie(
        pay,
        names='payment_method',
        values='quantity',
        hole=0.4,
        title="Quantity by Payment Method"
    )
    col2.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TAB 2 — TREND ANALYSIS
# -----------------------------
with tabs[1]:

    st.subheader("📈 Revenue Trend")

    trend = filtered_df.groupby(
        filtered_df['order_datetime'].dt.date
    )['line_value_aed'].sum().reset_index()

    fig = px.line(
        trend,
        x='order_datetime',
        y='line_value_aed',
        title="Daily Revenue"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 3 — CATEGORY ANALYSIS
# -----------------------------
with tabs[2]:

    st.subheader("📦 Category Performance")

    cat = filtered_df.groupby('category')['line_value_aed'].sum().reset_index()

    fig = px.bar(
        cat,
        x='category',
        y='line_value_aed',
        title="Revenue by Category"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 4 — COMPARISON
# -----------------------------
with tabs[3]:

    st.subheader("⚖️ City Comparison")

    comp = filtered_df.groupby('city')['line_value_aed'].sum().reset_index()

    fig = px.bar(
        comp,
        x='city',
        y='line_value_aed',
        color='city',
        title="Revenue by City"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 5 — DATA TABLE
# -----------------------------
with tabs[4]:

    st.subheader("📋 Data Table")
    st.dataframe(filtered_df)
