import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

# Set page configuration
st.set_page_config(layout="wide", page_title="Alpha Zone 2023 Dashboard")

# Your Supabase URL and key (replace with your actual values)
url = "https://cukweowdhbzfjqqufwns.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1a3dlb3dkaGJ6ZmpxcXVmd25zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMzA4NzgsImV4cCI6MjA0MTkwNjg3OH0.9BpDBshjSB54tbLVQ7MuSn7FopnnOp63FS9ASJ5pgps"

# Create a Supabase client
supabase: Client = create_client(url, key)

# Function to fetch all data from a table and return it as a DataFrame
@st.cache_data
def fetch_all_data_from_table(table_name, chunk_size=1000):
    """Fetch all rows from a Supabase table in batches to handle pagination."""
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
        st.warning(f"No data found for {table_name}")
        return pd.DataFrame()

# Fetch data for all tables
@st.cache_data
def load_data():
    tables = ['visits', 'orders', 'customers', 'items']
    data_frames = {}
    for table in tables:
        df = fetch_all_data_from_table(table)
        if not df.empty:
            data_frames[table] = df
    return data_frames

# Load all data
data = load_data()

# Function to categorize price levels
def categorize_price_level(price):
    if price > 12:
        return 'high'
    elif price < 5:
        return 'low'
    else:
        return 'medium'

# Add a new column 'price_level' based on the discount_price
data['orders']['price_level'] = data['orders']['discount_price'].apply(categorize_price_level)

# Main title
st.title("Alpha Zone 2023 Dashboard")

# Section 1: Sales by Category Filtered by Price Level
st.header("Sales by Category")

# Group by 'category' and 'price_level', sum 'discount_price' for sales
sales_by_category = data['orders'].groupby(['category', 'price_level'])['discount_price'].sum().reset_index()

# Create dropdown filter for 'price_level'
price_level_filter = st.selectbox("Select Price Level", ['All'] + list(sales_by_category['price_level'].unique()))

# Filter data based on selection
if price_level_filter != 'All':
    filtered_data = sales_by_category[sales_by_category['price_level'] == price_level_filter]
else:
    filtered_data = sales_by_category

# Create bar chart
fig1 = px.bar(filtered_data, x='category', y='discount_price', color='price_level',
              title="Sales by Category and Price Level",
              labels={'discount_price': 'Sales', 'category': 'Category'})
st.plotly_chart(fig1, use_container_width=True)

# Section 2 and 3: Top 5 Locations by Sales and Traffic Source by Duration
col1, col2 = st.columns(2)

with col1:
    st.header("Top 5 Locations by Sales")
    
    # Merge orders with customers to get 'location' column
    orders_with_location = pd.merge(data['orders'], data['customers'], on='Customer_ID', how='left', suffixes=('', '_customer'))
    
    # Convert 'date' to datetime and extract month
    orders_with_location['date'] = pd.to_datetime(orders_with_location['date'])
    orders_with_location['month'] = orders_with_location['date'].dt.to_period('M')
    
    # Group by 'location' and 'month', sum 'discount_price' for sales
    sales_by_location = orders_with_location.groupby(['month', 'location'])['discount_price'].sum().reset_index()
    
    # Get unique months for filtering
    months = sales_by_location['month'].unique()
    
    # Create dropdown for month selection
    selected_month = st.selectbox("Select Month", months, format_func=lambda x: str(x))
    
    # Filter data for the selected month and get top 5 locations
    monthly_data = sales_by_location[sales_by_location['month'] == selected_month]
    top_5_locations = monthly_data.nlargest(5, 'discount_price')
    
    # Create pie chart
    fig2 = px.pie(top_5_locations, values='discount_price', names='location', 
                  title=f"Top 5 Locations by Sales for {selected_month}")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.header("Traffic Source by Duration")
    
    # Group data by traffic source and calculate total duration for each
    traffic_duration = data['visits'].groupby('traffic_source')['duration'].sum().reset_index()
    
    # Calculate percentage of total duration for each traffic source
    traffic_duration['percentage'] = (traffic_duration['duration'] / traffic_duration['duration'].sum()) * 100
    
    # Create pie chart
    fig3 = px.pie(traffic_duration, values='percentage', names='traffic_source',
                  title='Traffic Source by Duration Percentage',
                  labels={'percentage': 'Duration Percentage'})
    st.plotly_chart(fig3, use_container_width=True)

# Section 4: Visits by Location Filtered by Month
st.header("Visits by Location")

# Ensure 'date' is in datetime format and extract month/year for grouping
data['visits']['date'] = pd.to_datetime(data['visits']['date'], errors='coerce')
data['visits']['month'] = data['visits']['date'].dt.to_period('M')

# Group by 'location' and 'month', count visits
visits_by_location = data['visits'].groupby(['location', 'month'])['visit_ID'].count().reset_index(name='visit_count')

# Create dropdown filter for 'month'
month_filter = st.selectbox("Select Month", ['All'] + list(visits_by_location['month'].unique()), format_func=lambda x: str(x))

# Filter data based on selection
if month_filter != 'All':
    filtered_visits = visits_by_location[visits_by_location['month'] == month_filter]
else:
    filtered_visits = visits_by_location

# Create scatter plot
fig4 = px.scatter(filtered_visits, x='location', y='visit_count',
                  title="Visits by Location",
                  labels={'visit_count': 'Number of Visits', 'location': 'Location'})
st.plotly_chart(fig4, use_container_width=True)
