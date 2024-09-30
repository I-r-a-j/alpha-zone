import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from supabase import create_client, Client

# Streamlit page configuration
st.set_page_config(page_title="Alpha Zone 2023 Dashboard", layout="wide")

# Your Supabase URL and key (replace with your actual values)
url = "https://cukweowdhbzfjqqufwns.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1a3dlb3dkaGJ6ZmpxcXVmd25zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMzA4NzgsImV4cCI6MjA0MTkwNjg3OH0.9BpDBshjSB54tbLVQ7MuSn7FopnnOp63FS9ASJ5pgps"

# Create a Supabase client
supabase: Client = create_client(url, key)

# Function to fetch all data from a table and return it as a DataFrame
def fetch_all_data_from_table(table_name, chunk_size=1000):
    offset = 0
    all_data = []

    while True:
        response = supabase.table(table_name).select('*').range(offset, offset + chunk_size - 1).execute()
        if response.data:
            all_data.extend(response.data)
            offset += chunk_size
        else:
            break

    if all_data:
        return pd.DataFrame(all_data)
    else:
        return pd.DataFrame()

# List of table names
tables = ['visits', 'orders', 'customers', 'items']
data_frames = {}

# Fetch all data for each table
for table in tables:
    df = fetch_all_data_from_table(table)
    if not df.empty:
        data_frames[table] = df

visits = data_frames['visits']
orders = data_frames['orders']
customers = data_frames['customers']
items = data_frames['items']

# Function to categorize price levels
def categorize_price_level(price):
    if price > 12:
        return 'high'
    elif price < 5:
        return 'low'
    else:
        return 'medium'

# Add a new column 'price_level' based on the discount_price
orders['price_level'] = orders['discount_price'].apply(categorize_price_level)

# Streamlit layout
st.title("Alpha Zone 2023 Dashboard")

# Section 1: Sales by Category with Price Level filter
st.subheader("Sales by Category Filtered by Price Level")
sales_by_category = orders.groupby(['category', 'price_level'])['discount_price'].sum().reset_index()
price_levels = sales_by_category['price_level'].unique()

# Streamlit selectbox for Price Level
selected_price_level = st.selectbox("Select Price Level", options=["All"] + list(price_levels))

# Filter data based on selected price level
fig = go.Figure()
for price_level in price_levels:
    filtered_data = sales_by_category[sales_by_category['price_level'] == price_level]
    fig.add_trace(go.Bar(
        x=filtered_data['category'],
        y=filtered_data['discount_price'],
        name=f"Price Level: {price_level}"
    ))

fig.update_layout(
    title="Sales by Category",
    xaxis_title="Category",
    yaxis_title="Sales (Discount Price)"
)

# Display plot
st.plotly_chart(fig)

# Section 2: Top 5 Locations by Sales for each Month
orders = pd.merge(orders, customers, on='Customer_ID', how='left', suffixes=('', '_customer'))
orders['date'] = pd.to_datetime(orders['date'])
orders['month'] = orders['date'].dt.to_period('M')
sales_by_location = orders.groupby(['month', 'location'])['discount_price'].sum().reset_index()

# Streamlit selectbox for Months
st.subheader("Top 5 Locations by Sales")
months = sales_by_location['month'].unique()
selected_month = st.selectbox("Select Month", options=months)

# Get top 5 locations
top_5_data = sales_by_location[sales_by_location['month'] == selected_month].nlargest(5, 'discount_price')

# Display pie chart
fig = px.pie(top_5_data, values='discount_price', names='location', title=f"Top 5 Locations by Sales for {selected_month}")
st.plotly_chart(fig)

# Section 3: Traffic Source by Duration Percentage
st.subheader("Traffic Source by Duration")
traffic_duration = visits.groupby('traffic_source')['duration'].sum().reset_index()
traffic_duration['percentage'] = (traffic_duration['duration'] / traffic_duration['duration'].sum()) * 100

fig = px.pie(traffic_duration, values='percentage', names='traffic_source', title="Traffic Source by Duration Percentage")
st.plotly_chart(fig)

# Section 4: Visits by Location and Month
st.subheader("Visits by Location and Month")
visits['date'] = pd.to_datetime(visits['date'], errors='coerce')
visits['month'] = visits['date'].dt.to_period('M')

visits_by_location = visits.groupby(['location', 'month'])['visit_ID'].count().reset_index(name='visit_count')
selected_month_visits = st.selectbox("Select Month for Visits", options=months)

filtered_visits = visits_by_location[visits_by_location['month'] == selected_month_visits]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=filtered_visits['location'],
    y=filtered_visits['visit_count'],
    mode='markers'
))

fig.update_layout(
    title=f"Visits by Location for {selected_month_visits}",
    xaxis_title="Location",
    yaxis_title="Number of Visits"
)

st.plotly_chart(fig)
