import pandas as pd
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px

# ==================== Fungsi ====================

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_byage_df(df):
    byage_df = df.groupby(by="age_group").customer_id.nunique().reset_index()
    byage_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    byage_df['age_group'] = pd.Categorical(byage_df['age_group'], ["Youth", "Adults", "Seniors"])
    return byage_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

def create_bygender_df(df):
    bygender_df = (
        df.groupby("gender")
        .customer_id.nunique()
        .reset_index(name="customer_count")
    )
    return bygender_df

# ==================== Load Data ====================
all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_date", "delivery_date"]
all_df.sort_values(by="order_date", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/mhvvn/dashboard_streamlit/refs/heads/main/img/tshirt.png", width=80)
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# ==================== Filter Data ====================
main_df = all_df[(all_df["order_date"] >= pd.to_datetime(start_date)) & 
                 (all_df["order_date"] <= pd.to_datetime(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# ==================== Dashboard ====================
st.header('My Collection Dashboard :sparkles:')

st.subheader('Daily Orders')
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

# --- Daily Orders Chart ---
fig = px.line(
    daily_orders_df,
    x="order_date",
    y="order_count",
    markers=True,
    title="Daily Orders"
)
fig.update_layout(
    xaxis=dict(tickfont=dict(size=15)),
    yaxis=dict(tickfont=dict(size=20))
)
st.plotly_chart(fig, use_container_width=True)

# --- Best & Worst Performing Product ---
st.subheader("Best & Worst Performing Product")

# Best Product
fig = px.bar(
    sum_order_items_df.head(5),
    x="quantity_x",
    y="product_name",
    orientation="h",
    title="Best Performing Product"
)
st.plotly_chart(fig, use_container_width=True)

# Worst Product
fig = px.bar(
    sum_order_items_df.sort_values("quantity_x").head(5),
    x="quantity_x",
    y="product_name",
    orientation="h",
    title="Worst Performing Product"
)
st.plotly_chart(fig, use_container_width=True)

# --- Customer Demographics ---
st.subheader("Customer Demographics")

# By Gender
fig = px.bar(
    bygender_df.sort_values("customer_count", ascending=False),
    x="gender",
    y="customer_count",
    title="Number of Customers by Gender"
)
st.plotly_chart(fig, use_container_width=True)

# By Age
fig = px.bar(
    byage_df.sort_values("age_group", ascending=False),
    x="age_group",
    y="customer_count",
    title="Number of Customers by Age"
)
st.plotly_chart(fig, use_container_width=True)

# --- Customer by State ---
fig = px.bar(
    bystate_df.sort_values("customer_count", ascending=False),
    x="customer_count",
    y="state",
    orientation="h",
    title="Number of Customers by State"
)
st.plotly_chart(fig, use_container_width=True)
