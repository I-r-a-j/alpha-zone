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
            # If no more data, break out of the loop
            break

    # Convert the accumulated data to a DataFrame
    if all_data:
        return pd.DataFrame(all_data)
    else:
        print(f"No data found for {table_name}")
        return pd.DataFrame()  # Return an empty DataFrame if no data

# List of table names
tables = ['visits', 'orders', 'customers', 'items']

# Dictionary to hold DataFrames for each table
data_frames = {}

# Fetch all data for each table and store it in the dictionary
for table in tables:
    print(f"Fetching all data from table: {table}")
    df = fetch_all_data_from_table(table)
    if not df.empty:
        data_frames[table] = df
        print(f"Data from {table}:")
        print(df.head(), "\n")
    else:
        print(f"No data retrieved from {table}")

# Now you can access the data as DataFrames
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

# Set up the Streamlit app title
st.title("Alpha Zone 2023 Dashboard")

# Section 1: Chart in the first row of the dashboard
st.header("Sales by Category Filtered by Price Level")
# Create the first chart with filters
price_levels = ['high', 'medium', 'low']  # Assuming the price levels are predefined
selected_price_level = st.selectbox("Select Price Level", price_levels)

# Filter the data based on the selected price level
filtered_sales_by_category = sales_by_category[sales_by_category['price_level'] == selected_price_level]

fig1 = go.Figure()
for price_level in price_levels:
    filtered_data = sales_by_category[sales_by_category['price_level'] == price_level]
    fig1.add_trace(go.Bar(
        x=filtered_data['category'],
        y=filtered_data['discount_price'],
        name=f"Price Level: {price_level}",
    ))

# Display the chart in Streamlit
st.plotly_chart(fig1)

# Section 2: Chart in the second row (left side)
st.header("Top 5 Locations by Sales for Selected Month")
selected_month = st.selectbox("Select Month", months)
top_5_data = get_top_5_locations(sales_by_location, selected_month)

fig2 = px.pie(top_5_data, values='discount_price', names='location', title=f"Top 5 Locations by Sales for {selected_month}")
st.plotly_chart(fig2)

# Section 3: Chart in the second row (right side)
st.header("Traffic Source by Duration Percentage")
fig3 = px.pie(
    traffic_duration,
    values='percentage',
    names='traffic_source',
    title='Traffic Source by Duration Percentage',
    labels={'percentage': 'Duration Percentage'}
)
st.plotly_chart(fig3)

# Section 4: Chart in the third row
st.header("Visits by Location Filtered by Month")
selected_month_visits = st.selectbox("Select Month for Visits", months)
filtered_visits_data = visits_by_location[visits_by_location['month'] == selected_month_visits]

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=filtered_visits_data['location'],
    y=filtered_visits_data['visit_count'],
    mode='markers',
    name=f"Month: {selected_month_visits}",
))

st.plotly_chart(fig4)
