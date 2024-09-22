import streamlit as st
import pandas as pd

from supabase import create_client, Client

# Your Supabase URL and key (replace with your actual values)
url = "https://cukweowdhbzfjqqufwns.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1a3dlb3dkaGJ6ZmpxcXVmd25zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMzA4NzgsImV4cCI6MjA0MTkwNjg3OH0.9BpDBshjSB54tbLVQ7MuSn7FopnnOp63FS9ASJ5pgps"

# Create a Supabase client
supabase: Client = create_client(url, key)

