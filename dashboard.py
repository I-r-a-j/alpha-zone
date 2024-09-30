import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

# Your Supabase URL and key (replace with your actual values)
url = "https://cukweowdhbzfjqqufwns.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1a3dlb3dkaGJ6ZmpxcXVmd25zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMzA4NzgsImV4cCI6MjA0MTkwNjg3OH0.9BpDBshjSB54tbLVQ7MuSn7FopnnOp63FS9ASJ5pgps"

# Create a Supabase client
supabase: Client = create_client(url, key)

# Function to fetch all data from a table and return it as a DataFrame
def fetch_all_data_from_table(table_name, chunk_size=1000):
    """Fetch all rows from a Supabase table in batches to handle pagination."""
    offset = 0
    all_data = []

    while True:
        # Fetch data in chunks
        response = supabase.table(table_name).select('*').range(offset, offset + chunk_size - 1).execute()

        # Check if data was returned
        if response.data:
            all_data.extend(response.data)  # Append the new data to the list
            offset += chunk_size  # Move the offset to fetch the next chunk
        else:
            break

    if all_data:
        return pd.DataFrame(all_data)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data

# List of table names
tables = ['visits', 'orders', 'customers', 'items']

# Dictionary to hold DataFrames for each table
data_frames = {}

# Fetch all data for each table and store it in the dictionary
for table in tables:
    df = fetch_all_data_from_table(table)
    if not df.empty:
        data_frames[table] = df

# Accessing data from Supabase tables as DataFrames
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

# Create the 'sales_by_category' DataFrame from 'orders' and 'items'
sales_by_category = pd.merge(orders, items, on='Item_ID', how='left')

# Define available months for sales and visits
months = ['January', 'February', 'March', 'April', 'May']

# Sidebar filters
st.sidebar.header("Filters")

# Price level filter
price_levels = ['high', 'medium', 'low']
selected_price_level = st.sidebar.selectbox("Select Price Level", price_levels)

# Month filter for sales
selected_month_sales = st.sidebar.selectbox("Select Month for Sales", months)

# Month filter for visits
selected_month_visits = st.sidebar.selectbox("Select Month for Visits", months)

# Set up the Streamlit app title
st.title("Alpha Zone 2023 Dashboard")

# Section 1: Sales by Category Filtered by Price Level
st.header("Sales by Category Filtered by Price Level")

# Filter the sales data by price level
filtered_sales_by_category = sales_by_category[sales_by_category['price_level'] == selected_price_level]

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=filtered_sales_by_category['category'],
    y=filtered_sales_by_category['discount_price'],
    name=f"Price Level: {selected_price_level}",
))

# Display the chart in Streamlit
st.plotly_chart(fig1)

# Section 2: Top 5 Locations by Sales for Selected Month
st.header(f"Top 5 Locations by Sales for {selected_month_sales}")
sales_by_location = visits.groupby(['location', 'month']).sum().reset_index()  # Create sales by location

# Filter data by selected month
top_5_data = sales_by_location[sales_by_location['month'] == selected_month_sales].nlargest(5, 'discount_price')

fig2 = px.pie(top_5_data, values='discount_price', names='location', title=f"Top 5 Locations by Sales for {selected_month_sales}")
st.plotly_chart(fig2)

# Section 3: Traffic Source by Duration Percentage
st.header("Traffic Source by Duration Percentage")
traffic_duration = visits.groupby('traffic_source').size().reset_index(name='percentage')

fig3 = px.pie(
    traffic_duration,
    values='percentage',
    names='traffic_source',
    title='Traffic Source by Duration Percentage'
)
st.plotly_chart(fig3)

# Section 4: Visits by Location Filtered by Month
st.header(f"Visits by Location for {selected_month_visits}")

# Filter visits by selected month
filtered_visits_data = visits[visits['month'] == selected_month_visits]

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=filtered_visits_data['location'],
    y=filtered_visits_data['visit_count'],
    mode='markers',
    name=f"Month: {selected_month_visits}",
))

st.plotly_chart(fig4)
