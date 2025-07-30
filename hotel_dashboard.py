import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 📥 DATA LOAD
# --------------------------------------------------
df = pd.read_csv("hotel_bookings.csv")
# Month order for correct chronological sorting
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# --------------------------------------------------
# 🎛 SIDEBAR FILTERS
# --------------------------------------------------
years = sorted(df['arrival_date_year'].unique())
months = list(df['arrival_date_month'].unique())
countries_list = list(df['country'].unique())

st.sidebar.header("🔎 Filter Options")
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
selected_months = st.sidebar.multiselect("Select Month(s)", months, default=months)
selected_countries = st.sidebar.multiselect(
    "Select Country(s)", countries_list,
    default=["PRT", "GBR", "FRA", "ESP", "DEU"]
)

# --------------------------------------------------
# 📄 DATA FILTERING
# --------------------------------------------------
filtered_df = df[
    (df['arrival_date_year'].isin(selected_years)) &
    (df['arrival_date_month'].isin(selected_months)) &
    (df['country'].isin(selected_countries))
]

# --------------------------------------------------
# 🏨 DASHBOARD TITLE
# --------------------------------------------------
st.title("🏨 Lisboa Hotel Booking Dashboard")

# --------------------------------------------------
# 🚨 EMPTY DATAFRAME CHECK
# --------------------------------------------------
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your filter selections.")
    st.stop()

# --------------------------------------------------
# 📊 KPI METRICS
# --------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Reservations", len(filtered_df))
col2.metric("Avg Lead Time", f"{filtered_df['lead_time'].mean():.1f} days")
col3.metric("Repeat Guest %", f"{(filtered_df['is_repeated_guest'].mean()*100):.1f}%")

col4, col5, col6 = st.columns(3)
prev_cancel_rate = filtered_df['previous_cancellations'].mean() * 100
total_customers = (
    filtered_df['adults'] + filtered_df['children'] + filtered_df['babies']
).sum()
avg_stay = (
    filtered_df['stays_in_weekend_nights'] + filtered_df['stays_in_week_nights']
).mean()
col4.metric("Previous Cancellation %", f"{prev_cancel_rate:.1f}%")
col5.metric("Total Customers", int(total_customers))
col6.metric("Avg Stay Duration", f"{avg_stay:.1f} nights")

col7, col8 = st.columns(2)
unique_agents = filtered_df['agent'].nunique()
most_common_country = filtered_df['country'].value_counts().idxmax()
col7.metric("Number of Agents", unique_agents)
col8.metric("Top Country", most_common_country)

# --------------------------------------------------
# 📈 MONTHLY BOOKINGS VS CANCELLATIONS
# --------------------------------------------------
monthly_stats = (
    filtered_df
    .groupby(['arrival_date_month', 'is_canceled'])
    .size()
    .reset_index(name='count')
)
monthly_stats['arrival_date_month'] = pd.Categorical(
    monthly_stats['arrival_date_month'], categories=month_order, ordered=True
)
monthly_stats = monthly_stats.sort_values('arrival_date_month')
monthly_stats['Status'] = monthly_stats['is_canceled'].map({0: 'Not Canceled', 1: 'Canceled'})

st.subheader("📅 Monthly Bookings vs Cancellations")
fig_monthly = px.bar(
    monthly_stats,
    x='arrival_date_month',
    y='count',
    color='Status',
    barmode='group',
    labels={'arrival_date_month': 'Month', 'count': 'Number of Bookings'}
)
st.plotly_chart(fig_monthly, use_container_width=True)

# --------------------------------------------------
# 🌍 BOOKINGS BY COUNTRY (EUROPE MAP)
# --------------------------------------------------
country_stats = filtered_df['country'].value_counts().reset_index()
country_stats.columns = ['country', 'bookings']

fig_map = px.choropleth(
    country_stats,
    locations='country',
    locationmode='ISO-3',
    color='bookings',
    hover_name='country',
    color_continuous_scale='Viridis',
    title='Bookings by Country',
    scope='world'
)

st.plotly_chart(fig_map, use_container_width=True)
