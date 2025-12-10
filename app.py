import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Page Config
st.set_page_config(page_title="Pro E-Commerce Dashboard", layout="wide", page_icon="🛒")

# Set Seaborn Style
sns.set_theme(style="whitegrid")

# 2. Data Loader
@st.cache_data
def get_data():
    filename = "ecommerce_with_repeating.csv"
    folder = "data"
    
    # Check if file exists
    possible_paths = [os.path.join(folder, filename), filename]
    
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path, parse_dates=["order_date"])
            
    # If not found, GENERATE IT
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    target_path = os.path.join(folder, filename)
    
    # Create Dummy Data
    data = {
        "order_id": range(1000, 1500),
        "user_id": np.random.randint(1, 100, 500),
        "product_id": np.random.randint(100, 120, 500),
        "product_name": [f"Product {i}" for i in np.random.randint(1, 11, 500)],
        "category": [["Electronics", "Fashion", "Home", "Beauty"][i] for i in np.random.randint(0, 4, 500)],
        "price": np.random.randint(50, 500, 500),
        "quantity": np.random.randint(1, 5, 500),
        "order_date": pd.date_range(start="2024-01-01", periods=500, freq="h"),
        "rating": np.random.randint(1, 6, 500),
        "is_repeating_customer": np.random.choice([True, False], 500)
    }
    df = pd.DataFrame(data)
    df.to_csv(target_path, index=False)
    return df

# Load Data
df_original = get_data()

# Preprocessing
df_original["revenue"] = df_original["quantity"] * df_original["price"]
df_original["order_day"] = df_original["order_date"].dt.date
df_original["order_hour"] = df_original["order_date"].dt.hour

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

# Date Filter
min_date = df_original["order_date"].min().date()
max_date = df_original["order_date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Category Filter
categories = df_original["category"].unique()
selected_categories = st.sidebar.multiselect(
    "Select Category", 
    options=categories, 
    default=categories
)

# Apply Filters
df = df_original[
    (df_original["order_day"] >= start_date) & 
    (df_original["order_day"] <= end_date) &
    (df_original["category"].isin(selected_categories))
]

# --- DASHBOARD ---
st.title("🛒 Pro E-Commerce Dashboard")

if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# KPIs
total_rev = df["revenue"].sum()
total_orders = df["order_id"].nunique()
avg_val = df["revenue"].mean()
repeat_rate = df["is_repeating_customer"].mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue", f"₹{total_rev:,.2f}")
c2.metric("📦 Total Orders", total_orders)
c3.metric("🏷️ Avg Order Value", f"₹{avg_val:,.2f}")
c4.metric("🔁 Repeat Rate", f"{repeat_rate:.1f}%")

st.divider()

# ROW 1: Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Revenue Trend")
    daily = df.groupby("order_day", as_index=False)["revenue"].sum()
    
    # Matplotlib/Seaborn Line Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=daily, x="order_day", y="revenue", marker='o', ax=ax)
    ax.set_ylabel("Revenue")
    ax.set_xlabel("Date")
    plt.xticks(rotation=45)
    st.pyplot(fig)

with col2:
    st.subheader("🥧 Revenue by Category")
    cat_rev = df.groupby("category", as_index=False)["revenue"].sum()
    
    # Matplotlib Pie Chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(cat_rev["revenue"], labels=cat_rev["category"], autopct="%1.1f%%", startangle=140)
    st.pyplot(fig)

# ROW 2: More Charts
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader("🏆 Top 5 Products")
    top = df.groupby("product_name", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).head(5)
    
    # Seaborn Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=top, x="revenue", y="product_name", ax=ax, palette="viridis")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Product Name")
    st.pyplot(fig)

with col4:
    st.subheader("⏰ Peak Hours")
    hourly = df.groupby("order_hour", as_index=False)["order_id"].count()
    
    # Seaborn Bar Chart for Hours
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(data=hourly, x="order_hour", y="order_id", ax=ax, palette="magma")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Orders")
    st.pyplot(fig)
