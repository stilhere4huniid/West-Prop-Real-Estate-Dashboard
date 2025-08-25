import os
import sys
import streamlit as st

# Add the current directory to the path so we can import the main app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the page config (this must be the first Streamlit command)
st.set_page_config(
    page_title="WestProp ROI Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the main app after setting up the environment
from real_estate_dashboard import main

if __name__ == "__main__":
    main()
