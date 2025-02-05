# Alpha Zone Business Website - Data Analysis Project
**Overview**
This project focuses on analyzing user interactions, traffic, and sales performance for the Alpha Zone business website for 2024. The analysis involves working with data from customer visits, orders, and products, utilizing SQL for data cleaning and transformation, and Python (with Streamlit and Plotly) for interactive dashboard creation.
you can visit it by this url:
[alpha zone dashboard](https://alpha-zone.streamlit.app/)



**Key Objectives:**
Data Cleaning: Handle missing values, remove unused fields, and update key columns for better analysis.
Traffic Source Analysis: Analyze visits based on traffic source and location.
Sales and Discounts: Explore sales trends, including the impact of discounts during certain months.
Interactive Dashboard: Provide real-time insights into business performance through visualizations.
**Project Structure**
SQL Queries
Categorization of Landing Pages: Categorize landing pages into ‘blog’, ‘shop’, or ‘other’ for simplified analysis.

Data Cleaning and Transformation:

Replace missing values in the visits table using the mode for categorical fields and the average for numeric fields.
Remove unnecessary columns from the customers table to streamline the data.
Order and Item Updates:

Add product details (e.g., category, regular_price) to the orders table.
Update order prices with a 10% discount for even months.
Traffic Source and Sales Summaries:

Analyze visits by traffic source, location, and duration.
Summarize monthly visits and sales, including categorizing months as "Discount" or "Non-Discount" based on pricing strategy.
Python Script (Streamlit Dashboard)
Data Fetching: Retrieves data from Supabase using a caching function for improved performance.

Interactive Dashboard: Visualizes key metrics such as:

Sales by category and price level.
Top locations by sales and traffic sources by duration.
Visits by location, filtered by month.
Plotly Visualizations:

Bar charts for sales, pie charts for location-based sales and traffic source duration, and scatter plots for visit trends.
Customization: Dropdown filters allow users to explore data by month and view sales performance based on different parameters.

Dashboard Features:
Sales by Category and Price Level: Visualize sales for each category with an option to filter by month.
Top Locations by Sales: Explore the top 5 locations by sales for each month.
Traffic Source Analysis: Visualize the contribution of each traffic source to user engagement.
Visits by Location: Analyze user visits by location, filtered by the selected month.

**How to Run the Project**

Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/alpha-zone-data-analysis.git
cd alpha-zone-data-analysis
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Streamlit dashboard:

bash
Copy code
streamlit run dashboard.py
Supabase Integration:

Ensure your Supabase URL and key are correctly set in the Python script.
The script fetches data from the tables: visits, orders, customers, and items.

**Dataset**

The project utilizes the following tables:

Visits: Data on user interactions with the website.
Orders: Transaction data including order details, discount prices, and regular prices.
Customers: Customer information (with sensitive columns removed for privacy).
Items: Product details including category and pricing.

**Visualizations**

Sales by Category and Price Level: Displays sales data broken down by product category and price level (high, medium, low), with filtering by month.
Top Locations by Sales: Highlights the top-performing locations by sales, presented in an interactive pie chart.
Traffic Source by Duration: Analyzes which traffic sources contribute the most engagement in terms of user session duration.
Visits by Location: Scatter plot showcasing website visits across different locations.

**Conclusion**

This project provides valuable insights into the performance of the Alpha Zone business, including traffic source analysis, sales trends, and customer engagement. With interactive visualizations, the project enables business stakeholders to explore key metrics and make data-driven decisions.
