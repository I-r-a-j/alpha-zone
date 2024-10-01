import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Section 1: Sales by Category and Price Level Filtered by Month
st.header("Sales by Category and Price Level")

# Convert 'date' to datetime and extract month and year
data['orders']['date'] = pd.to_datetime(data['orders']['date'])
data['orders']['month'] = data['orders']['date'].dt.strftime('%Y-%m')

# Group by 'category', 'price_level', and 'month', sum 'discount_price' for sales
sales_by_category = data['orders'].groupby(['category', 'price_level', 'month'])['discount_price'].sum().reset_index()

# Create dropdown filter options for 'month'
months = sales_by_category['month'].unique()

# Create Plotly figure
fig1 = go.Figure()

# Add traces for each month
for month in months:
    filtered_data = sales_by_category[sales_by_category['month'] == month]
    fig1.add_trace(go.Bar(
        x=filtered_data['category'],
        y=filtered_data['discount_price'],
        name=f"Month: {month}",
        hoverinfo='x+y',
        text=filtered_data['price_level'],
        hovertemplate='<b>Category</b>: %{x}<br><b>Sales</b>: %{y}<br><b>Price Level</b>: %{text}'
    ))

# Customize layout for filter option
fig1.update_layout(
    title="Sales by Category and Price Level Filtered by Month",
    xaxis_title="Category",
    yaxis_title="Sales (Discount Price)",
    updatemenus=[
        {
            "buttons": [
                {
                    "label": "All Months",
                    "method": "update",
                    "args": [{"visible": [True] * len(months)}, {"title": "All Months"}]
                },
                *[
                    {
                        "label": month,
                        "method": "update",
                        "args": [
                            {"visible": [i == j for j in range(len(months))]},
                            {"title": f"Sales for {month}"}
                        ]
                    } for i, month in enumerate(months)
                ]
            ],
            "direction": "down",
            "showactive": True,
        }
    ]
)

st.plotly_chart(fig1, use_container_width=True)

# Section 2 and 3: Top 5 Locations by Sales and Traffic Source by Duration
col1, col2 = st.columns(2)

with col1:
    st.header("Top 5 Locations by Sales")
    
    # [Code for Top 5 Locations by Sales remains unchanged]

with col2:
    st.header("Traffic Source by Duration")
    
    # Convert the 'date' column to datetime if it's not already
    data['visits']['date'] = pd.to_datetime(data['visits']['date'])

    # Extract month and year
    data['visits']['month_year'] = data['visits']['date'].dt.strftime('%B %Y')

    # Get unique months in 2023
    months_2023 = data['visits'][data['visits']['date'].dt.year == 2023]['month_year'].unique()

    # Create dropdown for month selection
    selected_month = st.selectbox("Select Month", months_2023, key="traffic_source_month")

    # Filter data for the selected month
    month_data = data['visits'][data['visits']['month_year'] == selected_month]
    
    # Group data by traffic source and calculate total duration for each
    traffic_duration = month_data.groupby('traffic_source')['duration'].sum().reset_index()
    
    # Calculate percentage of total duration for each traffic source
    traffic_duration['percentage'] = (traffic_duration['duration'] / traffic_duration['duration'].sum()) * 100
    
    # Create the pie chart
    fig3 = px.pie(
        traffic_duration, 
        values='percentage', 
        names='traffic_source',
        title=f'Traffic Source by Duration Percentage - {selected_month}'
    )

    # Show the chart
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
