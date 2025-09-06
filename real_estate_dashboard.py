# First, import necessary modules for page configuration
import streamlit as st
from PIL import Image  # Import Image before using it in set_page_config
from functools import lru_cache
import time

# Set page configuration
st.set_page_config(
    page_title="WestProp - Real Estate Dashboard",
    page_icon=Image.open("westprop_logo.png"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Other imports
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import folium
import datetime
from datetime import datetime as dt
import altair as alt
import random
import csv
import os
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import joblib  # For loading trained model and transformer
from io import BytesIO  # For PDF generation
from reportlab.lib.pagesizes import A4  # For PDF generation
from reportlab.pdfgen import canvas  # For PDF generation
from reportlab.lib.utils import ImageReader  # For PDF generation
import io  # For PDF generation
import json  # For handling JSON data
import smtplib  # For email functionality
import time  # For time-related functions
from email.message import EmailMessage  # For email functionality
import numpy as np  # For numerical operations, especially with dummy coordinates

# Initialize and optimize session state variables
def init_session_state():
    # Core session state variables
    defaults = {
        'is_admin': False,
        'form_submitted': False,
        'pending_email': None,
        'property_page': 1,
        'last_calculation': None,
        'cached_results': {},
        'filters': {}
    }
    
    # Only set defaults if they don't exist
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize session state
init_session_state()

# Cache for expensive calculations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_result(key, func, *args, **kwargs):
    return func(*args, **kwargs)

# Admin login/logout in sidebar
with st.sidebar:
    st.markdown("### 🔐 Admin Login")
    st.caption("Access required for managing subscribers and system settings")
    
    # Show different UI based on login state
    if st.session_state.is_admin:
        st.info("🔓 Admin access active - You can now manage subscribers")
        if st.button("Logout Admin"):
            st.session_state.is_admin = False
            # Reset page to Simulator when logging out
            st.session_state.page = "🏠 Simulator"
            st.rerun()
    else:
        with st.expander("Admin Login", expanded=False):
            password = st.text_input("Enter Admin Password:", 
                                  type="password", 
                                  key="admin_pwd",
                                  help="Contact IT support if you need admin access")
            if st.button("Login"):
                if password == "westprop2025":  # Change this to a secure password in production
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
    st.markdown("---")  # Add a separator

# Property details mapping
property_details = {
    # Radisson Aparthotel
    'radisson_details': {
        'name': 'Radisson Aparthotel',
        'type': 'Serviced Apartments',
        'price': 'From $120,000',
        'roi': '10-12% p.a.',
        'rental_yield': '8.5%',
        'location': 'Borrowdale, Harare',
        'status': 'Ready for Occupation',
        'description': 'Luxury serviced apartments with premium amenities and hotel services.',
        'images': ['project_images/radisson_apartments.webp'],
        'highlights': [
            '24/7 Security and Concierge',
            'Swimming Pool and Gym',
            'Housekeeping Services',
            'High-Speed Internet',
            'Restaurant and Bar',
            'Conference Facilities'
        ],
        'amenities': [
            'Air Conditioning',
            'Fully Equipped Kitchen',
            'Smart TV',
            'Laundry Services',
            'Underground Parking',
            'Backup Solar'
            'State of the art Gym',
            'Concierge Services',
            'Swimming Pool & Spa',
            'On-site Restaurant & Kitchen'
        ],
        'specs': {
            'Unit Sizes': '45-120 sqm',
            'Bedrooms': 'Studio, 1, 2, 3 Bed',
            'Bathrooms': '1-3',
            'Floors': '3',
            'Completion': 'Before thend of 2026',
            'Developer': 'WestProp Holdings',
            'Units': '148',
            'Parking': '2 per unit',
            'Security': '24/7 Armed Response',
            'Backup Power': 'Yes',
            'Water': 'Borehole + Mains'
        },
        'developer': 'WestProp Holdings',
        'completion': 'Before the end of 2026',
        'units': '120',
        'floors': '15',
        'yield': '8.5%',
        'payment_plan': 'Low-entry ownership from just $500 per unit',
        'contact': 'sales@westprop.com | +263 837 701 0170'
    },
    # Add other property details here...
    'pomona_details': {
        'name': 'Pomona City Flats',
        'type': '1-3 Bed Apartments',
        'price': 'From $70,000',
        'roi': '8-10% p.a.',
        'rental_yield': '7.5%',
        'location': 'Pomona, Harare',
        'status': 'Under Construction',
        'description': 'Modern, affordable apartments in a growing neighborhood with smart home features.',
        'images': ['project_images/pomona_city_flats.jpeg'],
        'highlights': [
            'Smart Home Features',
            'Gated Community',
            'Swimming Pool',
            'Children\'s Play Area',
            '24/7 Security',
            'Backup Power'
        ],
        'amenities': [
            'Gym',
            'Clubhouse',
            'Visitor Parking',
            'Landscaped Gardens',
            'CCTV',
            'Borehole Water'
        ],
        'specs': {
            'Unit Sizes': '45-90 sqm',
            'Bedrooms': '1-2',
            'Bathrooms': '1-2',
            'Floors': '8',
            'Completion': 'TBA',
            'Developer': 'WestProp Holdings',
            'Units': '380',
            'Parking': '1-2 per unit',
            'Security': '24/7 Guarded',
            'Backup Power': 'Yes',
            'Water': 'Borehole + Mains'
        },
        'developer': 'WestProp Holdings',
        'completion': 'TBA',
        'units': '200',
        'floors': '4',
        'yield': '7.5%',
        'payment_plan': '30% upfront deposit, Balance payable over 18 months, 1.25% monthly interest from Month 3',
        'early_bird_discounts': {
            '3% Discount': '30% deposit, 12-month plan (interest starts Month 6)',
            '5% Discount': '50% deposit, 6-month plan (no interest)'
        },
        'contact': 'sales@westprop.com | +263 837 701 0170'
    },
    'millennium_details': {
        'name': 'Millennium Heights',
        'type': 'Luxury Apartments',
        'price': 'From $65,000 to $310,000',
        'roi': '9-11% p.a.',
        'rental_yield': '8.2%',
        'location': 'Borrowdale, Harare',
        'status': 'Ready for Occupation',
        'description': 'Premium luxury apartments with high-end finishes and panoramic city views.',
        'images': ['project_images/millennium_heights_b4.jpeg'],
        'highlights': [
            'Premium Finishes',
            'Panoramic Views',
            'Swimming Pool',
            'Fitness Center',
            'Biometric security, & 24/7 Security',
            'Backup Power & Water',
            'Gym, ttennis, & basketball courts'
        ],
        'amenities': [
            'Concierge',
            'Visitor Parking',
            'Landscaped Gardens',
            'CCTV',
            'Elevators',
            'Borehole Water'
        ],
        'specs': {
            'Unit Sizes': '60-200 sqm',
            'Bedrooms': '1-3',
            'Bathrooms': '1-3',
            'Floors': '4',
            'Completion': 'TBA-ongoing progress',
            'Developer': 'WestProp Holdings',
            'Units': '148',
            'Parking': '2 per unit',
            'Security': '24/7 Armed Response',
            'Backup Power': 'Yes',
            'Water': 'Borehole + Mains'
        },
        'developer': 'WestProp Holdings',
        'completion': 'TBA-ongoing progress',
        'units': '86',
        'floors': '6',
        'yield': '8.2%',
        'payment_plan': 'Flexible payment plans available',
        'contact': 'sales@westprop.com | +263 837 701 0170'
    },
    'pokugara_details': {
        'name': 'Pokugara Townhouses',
        'type': '3-4 Bed Townhouses',
        'price': 'From $357,000 to $409,000',
        'roi': '9-11% p.a.',
        'rental_yield': '8.0%',
        'location': 'Borrowdale, Harare',
        'status': 'Ready for Occupation',
        'description': 'Spacious townhouses with private gardens in an exclusive gated community.',
        'images': ['project_images/pokugara_townhouses.jpeg'],
        'highlights': [
            'Private Gardens',
            'Double Garage',
            'Maid\'s Quarters',
            '24/7 Security with CCTV',
            'Solar Backup Powere',
            'Borehole Water'
            'Metered LBG central gas connection'
            'Private Parking'
            'Turnkey handover with full fittings and finishes (Gas Stove, Tiled, Built In Cupboards, Fitted Kitchen, Walled/Fenced, Veranda, Landscaped Garden)'

        ],
        'amenities': [
            'Swimming Pool',
            'Clubhouse',
            'Children\'s Play Area',
            'Jogging Trails',
            'CCTV',
            'Visitor Parking'
            'Braai & Picnic area'
            'Tennis courts'
            'Clubhouse for social gatherings'
        ],
        'specs': {
            'Unit Sizes': '200-300 sqm',
            'Bedrooms': '3-4',
            'Bathrooms': '3-4',
            'Floors': '2',
            'Completion': '2023',
            'Developer': 'WestProp Holdings',
            'Units': '50',
            'Parking': '2-3 per unit',
            'Security': '24/7 Guarded',
            'Backup Power': 'Yes',
            'Water': 'Borehole + Mains',
            'Land Size': '300-500 sqm'
        },
        'developer': 'WestProp Holdings',
        'completion': 'Final stages, scheduled for handover in 2025',
        'units': '50',
        'floors': '2',
        'yield': '8.0%',
        'payment_plan': 'Flexible payment plans available',
        'contact': 'sales@westprop.com | +263 837 701 0170'
    },
    'hills_retirement': {
        'name': 'The Hills Lifestyle Estate',
        'type': '1-2 Bedroom Retirement Units',
        'price': 'From $100,000',
        'roi': '7-9% p.a.',
        'rental_yield': '6.5%',
        'location': 'The Hills, Harare',
        'status': 'Available',
        'description': 'Exclusive retirement living with premium amenities and healthcare services.',
        'images': ['project_images/the_hills_estate.png'],
        'highlights': [
            '24/7 Security',
            'Medical Alert System',
            'Community Center',
            'Healthcare Services',
            'Maintenance Included',
            'Social Activities'
        ],
        'amenities': [
            'Swimming Pool',
            'Fitness Center',
            'Library',
            'Dining Hall',
            'Gardens',
            'Emergency Response'
            'Art studios'
            'Peaceful gardens'
            'Spa'
        ],
        'specs': {
            'Unit Sizes': '60-100 sqm',
            'Bedrooms': '1-2',
            'Bathrooms': '1-2',
            'Floors': '1-2 (differs)',
            'Completion': 'Golf Course (mid-2026) & Overall Estate (by 2050 for the billion brick vision)',
            'Developer': 'WestProp Holdings',
            'Units': '119',
            'Parking': '1-2 per unit',
            'Security': '24/7 Guarded + CCTV',
            'Backup Power': 'Yes',
            'Water': 'Borehole + Mains',
            'Age Restriction': '55+'
        },
        'developer': 'WestProp Holdings',
        'completion': 'By 2050',
        'units': '119',
        'floors': '1-2 (differs)',
        'yield': '6.5%',
        'payment_plan': 'Flexible payment plans available',
        'contact': 'sales@westprop.com | +263 837 701 0170'
    },
    'hills_villas_details': {
        'name': 'The Hills Family Villas',
        'type': '4-5 Bed Villas',
        'price': 'From $350,000',
        'roi': '8-10% p.a.',
        'rental_yield': '7.5%',
        'location': 'The Hills, Harare',
        'status': 'Under Construction',
        'description': 'Luxury family villas with modern amenities and spacious living areas.',
        'images': ['project_images/the_hills_villas.jpeg'],
        'highlights': [
            'Spacious Layouts',
            'Private Gardens',
            'Maid\'s Quarters',
            'Double Garage',
            '24/7 Security',
            'Backup Power & Water'
        ],
        'amenities': [
            'Swimming Pool',
            'Clubhouse',
            'Tennis Court',
            'Children\'s Play Area',
            'Jogging Trails',
            'Visitor Parking'
        ],
        'specs': {
            'Unit Sizes': '250-350 sqm',
            'Bedrooms': '4-5',
            'Bathrooms': '3-4',
            'Floors': '2',
            'Completion': 'By 2050',
            'Developer': 'WestProp Holdings',
            'Units': '30',
            'Parking': '2-3 per unit',
            'Security': '24/7 Guarded + CCTV',
            'Backup Power': 'Yes',
            'Water': 'Borehole + Mains',
            'Land Size': '500-800 sqm'
        },
        'developer': 'WestProp Holdings',
        'completion': 'By 2050',
        'units': '30',
        'floors': '1-2 (differs)',
        'yield': '7.5%',
        'payment_plan': 'Flexible payment plans available',
        'contact': 'sales@westprop.com | +263 837 701 0170'
    },
    'pomona_stands_details': {
        'name': 'Pomona City Stands',
        'type': 'Residential Stands',
        'price': 'From $92,950',
        'roi': 'N/A',
        'rental_yield': 'N/A',
        'location': 'Pomona, Harare',
        'status': 'Available',
        'description': 'Prime residential stands in a well-planned development with all necessary infrastructure.',
        'images': ['pomona_city_stands.jpeg'],
        'highlights': [
            'Fully Serviced',
            'Tarred Roads',
            'Water & Sewer',
            'Electricity',
            'Security',
            'Prime Location'
        ],
        'amenities': [
            'Shopping Center',
            'Schools',
            'Medical Facilities',
            'Recreational Parks',
            'Easy Access to CBD',
            'Public Transport'
        ],
        'specs': {
            'Stand Sizes': '300-1000 sqm',
            'Zoning': 'Residential',
            'Serviced': 'Yes',
            'Title Deeds': 'Available',
            'Development': 'Ongoing',
            'Completion': 'Ongoing'
        },
        'developer': 'WestProp Holdings',
        'completion': 'N/A',
        'units': '29',
        'floors': 'N/A',
        'yield': 'N/A',
        'payment_plan': 'Flexible payment plans available',
        'contact': 'sales@westprop.com | +263 837 701 0170'
    }
}

# Project profiles information
project_profiles_info = {
    "Pokugara Luxury Apartments": {
        'image': 'project_images/pokugara_townhouses.jpeg',
        'description': "Luxury apartments with premium finishes and stunning views in the heart of the city.",
        'url': '#'
    },
    "The Hills": {
        'image': 'project_images/millennium_heights_b4.jpeg',
        'description': "Exclusive hillside development offering modern living with panoramic city views.",
        'url': '#'
    },
    "Pomona City": {
        'image': 'project_images/pomona_city_flats.jpeg',
        'description': "Contemporary urban living with smart home features and excellent amenities.",
        'url': '#'
    }
}
from dotenv import load_dotenv # For loading environment variables (e.g., email credentials)
import seaborn as sns # For enhanced plots in Executive Summary

# Load environment variables from .env file
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Define data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Load smart feature value proposition table (from original dashboard)
smart_value_path = os.path.join(DATA_DIR, "smart_feature_value_table.csv")
smart_value_df = pd.read_csv(smart_value_path)

# --- CONFIG ---
st.image("westprop_logo.png", width=200)

# Load the trained model, transformer, and feature names
# Assuming these files are in the same directory as the dashboard script
model = joblib.load("models/roi_prediction_model.pkl")
pt = joblib.load("models/roi_transformer.pkl") # PowerTransformer for inverse transformation
model_features = joblib.load("models/model_features.pkl") # List of features the model was trained on

# Load the real estate data template with all calculated ROIs
real_estate_df = pd.read_csv("data/real_estate_data_template.csv")

# --- Smart Feature Savings (Updated based on research) ---
SMART_FEATURE_MULTIPLIER = 1.5  # Multiplier for smart feature impact
SOLAR_SAVINGS = 80  # USD per month
WATER_RECYCLING_SAVINGS = 25 # USD per month
SMART_LOCKS_SAVINGS = 10 # USD per month
SMART_THERMOSTATS_SAVINGS = 15 # USD per month
INTEGRATED_SECURITY_SAVINGS = 30 # USD per month
EV_CHARGING_SAVINGS = 20 # USD per month

# --- SESSION STATE DEFAULTS ---
if "market_price" not in st.session_state:
    st.session_state.market_price = 120000
if "monthly_rent" not in st.session_state:
    st.session_state.monthly_rent = 1000
if "has_solar" not in st.session_state:
    st.session_state.has_solar = True
# Ensure all smart features are initialized
if "has_water_recycling" not in st.session_state:
    st.session_state.has_water_recycling = False
if "has_smart_locks" not in st.session_state:
    st.session_state.has_smart_locks = False
if "has_smart_thermostats" not in st.session_state:
    st.session_state.has_smart_thermostats = False
if "has_integrated_security" not in st.session_state:
    st.session_state.has_integrated_security = False
if "has_ev_charging" not in st.session_state:
    st.session_state.has_ev_charging = False
if "selected_session_idx" not in st.session_state:
    st.session_state.selected_session_idx = 0

# Initialize ROI-related session states
if "roi" not in st.session_state:
    st.session_state.roi = 0.0
if "smart_roi" not in st.session_state:
    st.session_state.smart_roi = 0.0
if "predicted_roi_original" not in st.session_state:
    st.session_state.predicted_roi_original = 0.0
if "annual_savings_total" not in st.session_state:
    st.session_state.annual_savings_total = 0.0
if "roi_chart_buf" not in st.session_state:
    st.session_state.roi_chart_buf = None

# --- Property Data Structure (from original dashboard) ---
# This data is now primarily for the Project Profiles page, as the Property Browser
# and ROI Map use the real_estate_df loaded from CSV.
properties_data = [
    {
        "project": "The Hills Lifestyle Estate",
        "property_type": "Villa - 4 Bed",
        "price": 380000, # Starting price might vary
        "size_sqm": None, # Add if known
        "bedrooms": 4,
        "status": "Selling",
        "amenities": ["Golf Access", "Mall Access", "Wellness Center", "Security", "Scenic Views"],
        "payment_terms": "30% Deposit, $10k Commit, 24mo Balance (Interest from Mo 6)",
        "roi_projected": None, # Placeholder
        "url": "https://www.westprop.com/developments/the-hills/"
    },
    {
        "project": "The Hills Lifestyle Estate",
        "property_type": "Villa - 5 Bed",
        "price": 500000, # Example starting price
        "size_sqm": None, # Add if known
        "bedrooms": 5,
        "status": "Selling",
        "amenities": ["Golf Access", "Mall Access", "Wellness Center", "Security", "Scenic Views"],
        "payment_terms": "30% Deposit, $10k Commit, 24mo Balance (Interest from Mo 6)",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/the-hills/"
    },
     {
        "project": "The Hills Lifestyle Estate",
        "property_type": "Residential Stand",
        "price": 70000, # Starting price
        "size_sqm": 2000, # Example size
        "bedrooms": None,
        "status": "Selling",
        "amenities": ["Golf Access", "Mall Access", "Wellness Center", "Security", "Scenic Views"],
        "payment_terms": "30% Deposit, $10k Commit, 24mo Balance (Interest from Mo 6)",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/the-hills/"
    },
    {
        "project": "Radisson Serviced Apartments",
        "property_type": "Serviced Apartment (REIT)",
        "price": 500, # Minimum REIT investment
        "size_sqm": None,
        "bedrooms": None, # Varies (Studio, 1/2 Bed, Penthouse)
        "status": "Selling via REIT",
        "amenities": ["Hotel Services", "Pool", "Gym", "Conference Facilities", "Security"],
        "payment_terms": "REIT Investment (Seatrite 5 Trust)",
        "roi_projected": 8.0, # Guaranteed USD return
        "url": "https://www.westprop.com/developments/millenium-serviced-apartments/" # Note: Link might be broken
    },
    {
        "project": "Millennium Heights Block 4",
        "property_type": "Apartment - Studio",
        "price": 65000, # Text price, table shows Sold Out
        "size_sqm": None,
        "bedrooms": 0,
        "status": "Sold Out", # Based on table
        "amenities": ["Pool", "Gym", "Clubhouse", "Security", "Solar", "Backup Water", "Lock-up Shell"],
        "payment_terms": "Flexible Payment Plan",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/millenium-heights/apartments-block-4/"
    },
    {
        "project": "Millennium Heights Block 4",
        "property_type": "Apartment - 1 Bed",
        "price": 110000, # Table price
        "size_sqm": 73,
        "bedrooms": 1,
        "status": "Selling",
        "amenities": ["Pool", "Gym", "Clubhouse", "Security", "Solar", "Backup Water", "Lock-up Shell"],
        "payment_terms": "Flexible Payment Plan",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/millenium-heights/apartments-block-4/"
    },
    {
        "project": "Millennium Heights Block 4",
        "property_type": "Apartment - 2 Bed",
        "price": 189000,
        "size_sqm": 116,
        "bedrooms": 2,
        "status": "Selling",
        "amenities": ["Pool", "Gym", "Clubhouse", "Security", "Solar", "Backup Water", "Lock-up Shell"],
        "payment_terms": "Flexible Payment Plan",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/millenium-heights/apartments-block-4/"
    },
    {
        "project": "Millennium Heights Block 4",
        "property_type": "Apartment - 3 Bed",
        "price": 310000,
        "size_sqm": None,
        "bedrooms": 3,
        "status": "Selling",
        "amenities": ["Pool", "Gym", "Clubhouse", "Security", "Solar", "Backup Water", "Lock-up Shell"],
        "payment_terms": "Flexible Payment Plan",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/millenium-heights/apartments-block-4/"
    },
    {
        "project": "Pokugara Townhouses",
        "property_type": "Townhouse - Garden",
        "price": 357000,
        "size_sqm": 190,
        "bedrooms": 4,
        "status": "Selling Off-Plan (Limited Units)",
        "amenities": ["Clubhouse", "Pool", "Gym", "Security", "Solar Provision", "Backup Water", "Private Garden"],
        "payment_terms": "30% Deposit, $1k Commit, 3-6mo Interest-Free",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/pokugara/"
    },
    {
        "project": "Pokugara Townhouses",
        "property_type": "Townhouse - Manor",
        "price": 409000,
        "size_sqm": 203,
        "bedrooms": 4,
        "status": "Selling Off-Plan (Final Unit)",
        "amenities": ["Clubhouse", "Pool", "Gym", "Security", "Solar Provision", "Backup Water", "Landscaping Space"],
        "payment_terms": "30% Deposit, $1k Commit, 3-6mo Interest-Free",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/pokugara/"
    },
    {
        "project": "Pomona City",
        "property_type": "Flat",
        "price": 125000,  # Example for 1,000 sqm stand (adjust as needed)
        "size_sqm": 69.72,
        "bedrooms": None,
        "status": "Selling",
        "amenities": [
            "Gated Community", "24/7 Security", "Smart Tech", "Solar Street Lighting",
            "Fiber Internet", "Tarred Roads", "Parks", "Water Reticulation", "Playgrounds"
        ],
        "payment_terms": "30% Deposit, Balance payable over 18 months, 1.25% monthly interest from Month 3, 3% Discount: 30% deposit, 12-month plan (interest starts Month 6), 5% Discount: 50% deposit, 6-month plan (no interest)",
        "roi_projected": None,
        "url": "https://www.westprop.com/developments/pomona-city-flats/"
    }
    # 
]

# Cache data loading and processing
@st.cache_data(ttl=3600)
def load_properties_data():
    return pd.DataFrame(properties_data)

# Convert to DataFrame for easier filtering
properties_df = load_properties_data()

# Extract unique values for filters
projects = sorted(properties_df["project"].unique())
property_types = sorted(properties_df["property_type"].unique())
statuses = sorted(properties_df["status"].unique())

# Get all unique amenities from the lists in the DataFrame
all_amenities = set()
for amenities_list in properties_df["amenities"].dropna():
    all_amenities.update(amenities_list)
amenities_options = sorted(list(all_amenities))

# --- Project Profiles Data (Images & Descriptions) ---
project_profiles_info = {
    "The Hills Lifestyle Estate": {
        "image": "project_images/the_hills_estate.png", # Adjusted path
        "description": "Zimbabwe's first integrated luxury golf estate offering villas and residential stands. Features include golf access, mall access, wellness center, and high security.",
        "url": "https://www.westprop.com/developments/the-hills/"
    },
    "Radisson Serviced Apartments": {
        "image": "project_images/radisson_apartments.webp", # Adjusted path
        "description": "Luxury serviced apartments managed by Radisson, available through the Seatrite 5 REIT. Offers hotel services, pool, gym, and conference facilities with guaranteed returns.",
        "url": "https://www.westprop.com/developments/millenium-heights/radisson-serviced-apartments-harare-zimbabwe/"
    },
    "Millennium Heights Block 4": {
        "image": "project_images/millennium_heights_b4.jpeg", # Adjusted path
        "description": "Dubai-inspired luxury apartments in Borrowdale West. Offers studio to 3-bed units with amenities like pool, gym, clubhouse, solar, and backup water. Lock-up shell options available.",
        "url": "https://www.westprop.com/developments/millenium-heights/apartments-block-4/"
    },
    "Pokugara Townhouses": {
        "image": "project_images/pokugara_townhouses.jpeg", # Adjusted path
        "description": "Modern 4-bedroom townhouses (Garden & Manor types) in a secure gated community in Borrowdale West. Features include clubhouse, pool, gym, solar provision, and private gardens/landscaping space.",
        "url": "https://www.westprop.com/developments/pokugara/"
    },
    "Pomona City": {
        "image": "project_images/pomona_city_flats.jpeg",
        "description": "A city within a city offering residential stands (800m² - 1,000m²) in a smart, gated community. Blends technology, modern luxury, and nature.",
        "url": "https://www.westprop.com/developments/residential-stands-in-pomona-city/"
    }
    # Add profiles for Pomona City, Warren Hills etc. when data is available
}




# --- Navigation ---
st.sidebar.title("📂 Navigate")
pages = [
    "🏠 Simulator", "🗂️ My Simulations", "📈 Executive Summary", "🗺️ ROI Map", "📍 Project Profiles",
    "📊 Investment Models", "💸 Payment Plan Calculator", "🔍 Property Browser",
    "🧬 Investor Match", "🔧 Shell Unit Customizer", "♻️ Smart Feature Value Proposition",
    "❓ Help", "ℹ️ About", "🔔 Alerts", "🏆 Community Insights", "📉 Market Trends & Analytics",
    "🛡️ Admin Analytics"
]

page = st.sidebar.radio("Go to", pages, key="page")

# --- Simulator Page ---
if page == "🏠 Simulator":
    st.title("🏡 Smart Real Estate ROI Simulator")
    st.markdown("Simulate the ROI impact of adding smart features to your property.")

    # Initialize form key in session state if not exists
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
        
    # Create a form with a unique key that changes when project is selected
    with st.sidebar.form(key=f'simulator_form_{st.session_state.form_key}'):
        st.header("⚙️ Simulate Your Property")
        market_price = st.number_input(
            "Market Price (USD)",
            min_value=0.0,
            value=float(st.session_state.get('market_price', 100000.0)),
            step=1000.0,
            help="The total purchase price of the property"
        )
        monthly_rent = st.number_input(
            "Expected Monthly Rent (USD)",
            min_value=0.0,
            value=float(st.session_state.get('monthly_rent', 1000.0)),
            step=50.0,
            help="Expected monthly rental income"
        )
        st.subheader("Smart Features")
        has_solar = st.checkbox(
            "☀️ Has Solar",
            value=st.session_state.has_solar,
            help="Adds rooftop solar panels. Boosts savings and ROI."
        )
        has_water_recycling = st.checkbox(
            "💧 Has Water Recycling",
            value=st.session_state.has_water_recycling,
            help="Includes greywater systems for irrigation or reuse."
        )
        has_smart_locks = st.checkbox(
            "🔐 Has Smart Locks",
            value=st.session_state.has_smart_locks,
            help="Improves security with digital locks. Adds value to rentals."
        )
        has_smart_thermostats = st.checkbox(
            "🌡️ Has Smart Thermostats",
            value=st.session_state.has_smart_thermostats,
            help="Optimizes heating/cooling for energy savings."
        )
        has_integrated_security = st.checkbox(
            "🚨 Has Integrated Security",
            value=st.session_state.has_integrated_security,
            help="Comprehensive security systems (alarms, cameras, sensors)."
        )
        has_ev_charging = st.checkbox(
            "🔌 Has EV Charging",
            value=st.session_state.has_ev_charging,
            help="Electric Vehicle charging infrastructure."
        )

        # Additional features needed for prediction
        bedrooms = st.number_input("Number of Bedrooms", min_value=1, value=3, step=1)
        bathrooms = st.number_input("Number of Bathrooms", min_value=1, value=2, step=1)
        stand_size_sqm = st.number_input("Stand Size (sqm)", min_value=100, value=500, step=50)
        building_size_sqm = st.number_input("Building Size (sqm)", min_value=50, value=200, step=25)

        # Location and Property Type (for prediction, need to match model_features)
        # Use unique values from your real_estate_df for selectboxes
        location_suburb = st.selectbox("Location Suburb", real_estate_df["location_suburb"].unique(), index=0)
        property_type = st.selectbox("Property Type", real_estate_df["property_type"].unique(), index=0)

        submit_sim = st.form_submit_button("Update Simulation")

    # Only update session state and save snapshot when form is submitted
    if submit_sim:
        st.session_state.market_price = market_price
        st.session_state.monthly_rent = monthly_rent
        st.session_state.has_solar = has_solar
        st.session_state.has_water_recycling = has_water_recycling
        st.session_state.has_smart_locks = has_smart_locks
        st.session_state.has_smart_thermostats = has_smart_thermostats
        st.session_state.has_integrated_security = has_integrated_security
        st.session_state.has_ev_charging = has_ev_charging

        # --- Prepare features for model prediction ---
        input_data = {
            "stand_size_sqm": stand_size_sqm,
            "building_size_sqm": building_size_sqm,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sale_price_usd": market_price,
            "has_solar": int(has_solar),
            "has_water_recycling": int(has_water_recycling),
            "has_smart_locks": int(has_smart_locks),
            "has_smart_thermostats": int(has_smart_thermostats),
            "has_integrated_security": int(has_integrated_security),
            "has_ev_charging": int(has_ev_charging),
            "location_suburb": location_suburb,
            "property_type": property_type
        }

        # Create a DataFrame from input_data
        input_df = pd.DataFrame([input_data])

        # One-hot encode categorical features, aligning with model_features
        # Create dummy columns for all possible categories the model was trained on
        # This ensures that even if a category isn\\\"t present in input_df, its column exists with 0
        encoded_input_df = pd.get_dummies(input_df, columns=["location_suburb", "property_type"], drop_first=True)

        # Align columns - add missing columns (from model_features) with 0 and reorder
        final_input_df = pd.DataFrame(columns=model_features) # Create a df with all expected columns
        for col in model_features:
            if col in encoded_input_df.columns:
                final_input_df[col] = encoded_input_df[col]
            else:
                final_input_df[col] = 0 # Fill missing feature columns with 0
        
        # Ensure numerical columns are of correct type
        for col in ["stand_size_sqm", "building_size_sqm", "bedrooms", "bathrooms", "sale_price_usd"]:
            final_input_df[col] = pd.to_numeric(final_input_df[col])

        # Predict transformed ROI
        predicted_roi_transformed = model.predict(final_input_df)[0]

        # Inverse transform to get original ROI percentage
        predicted_roi_original = pt.inverse_transform(predicted_roi_transformed.reshape(-1, 1)).flatten()[0]

        # --- Calculate Traditional ROI and Smart ROI (for comparison) ---
        annual_rent = st.session_state.monthly_rent * 12
        
        # Expense rates (from calculate_roi.py)
        PROPERTY_TAX_RATE = 0.01
        MAINTENANCE_RATE = 0.015
        INSURANCE_RATE = 0.004
        AGENT_FEE_RATE = 0.10

        annual_property_tax_usd = st.session_state.market_price * PROPERTY_TAX_RATE
        annual_maintenance_usd = st.session_state.market_price * MAINTENANCE_RATE
        annual_insurance_usd = st.session_state.market_price * INSURANCE_RATE
        annual_agent_fees_usd = annual_rent * AGENT_FEE_RATE

        total_annual_expenses_usd = annual_property_tax_usd + annual_maintenance_usd + annual_insurance_usd + annual_agent_fees_usd
        net_annual_income_usd = annual_rent - total_annual_expenses_usd

        roi = (net_annual_income_usd / st.session_state.market_price) * 100 if st.session_state.market_price > 0 else 0

        # Calculate Smart ROI (considering smart feature savings)
        monthly_savings_total = (
            (SOLAR_SAVINGS if st.session_state.has_solar else 0)
            + (WATER_RECYCLING_SAVINGS if st.session_state.has_water_recycling else 0)
            + (SMART_LOCKS_SAVINGS if st.session_state.has_smart_locks else 0)
            + (SMART_THERMOSTATS_SAVINGS if st.session_state.has_smart_thermostats else 0)
            + (INTEGRATED_SECURITY_SAVINGS if st.session_state.has_integrated_security else 0)
            + (EV_CHARGING_SAVINGS if st.session_state.has_ev_charging else 0)
        )
        annual_savings_total = monthly_savings_total * 12

        net_annual_income_with_smart_savings = (annual_rent + annual_savings_total) - total_annual_expenses_usd
        smart_roi = (net_annual_income_with_smart_savings / st.session_state.market_price) * 100 if st.session_state.market_price > 0 else 0

        # --- Save snapshot to server log ---
        snapshot = {
            "Timestamp": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Market Price": st.session_state.market_price,
            "Monthly Rent": st.session_state.monthly_rent,
            "Has Solar": st.session_state.has_solar,
            "Has Water Recycling": st.session_state.has_water_recycling,
            "Has Smart Locks": st.session_state.has_smart_locks,
            "Has Smart Thermostats": st.session_state.has_smart_thermostats,
            "Has Integrated Security": st.session_state.has_integrated_security,
            "Has EV Charging": st.session_state.has_ev_charging,
            "Predicted ROI (Model)": round(predicted_roi_original, 2),
            "Traditional ROI (Calculated)": round(roi, 2),
            "Smart ROI (Calculated)": round(smart_roi, 2)
        }
        snapshot_df = pd.DataFrame([snapshot])
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "session_log.csv")
        snapshot_df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)

    # --- Load Past Simulation ---
    with st.expander("💾 Load Past Simulation", expanded=False):
        try:
            # Read the session log from the data directory
            session_log_path = os.path.join("data", "session_log.csv")
            if os.path.exists(session_log_path):
                session_df = pd.read_csv(session_log_path)
                
                # Filter out empty rows and format for display
                session_df = session_df.dropna(how='all')
                if not session_df.empty:
                    # Format the display text for each simulation
                    session_df['display'] = session_df.apply(
                        lambda row: f"{row['Timestamp']} - ${int(row['Market Price']):,} @ ${int(row['Monthly Rent']):,}/mo", 
                        axis=1
                    )
                    
                    # Show most recent first
                    session_df = session_df.sort_values('Timestamp', ascending=False)
                    
                    # Create a selectbox with the simulations
                    selected_sim = st.selectbox(
                        "Select a simulation to load:",
                        options=session_df.index,
                        format_func=lambda x: session_df.loc[x, 'display']
                    )
                    
                    if st.button("Load Selected Simulation"):
                        # Update session state with selected simulation
                        sim = session_df.loc[selected_sim]
                        st.session_state.market_price = float(sim['Market Price'])
                        st.session_state.monthly_rent = float(sim['Monthly Rent'])
                        st.session_state.has_solar = bool(sim['Has Solar'])
                        st.session_state.has_water_recycling = bool(sim['Has Water Recycling'])
                        st.session_state.has_smart_locks = bool(sim['Has Smart Locks'])
                        st.session_state.has_smart_thermostats = bool(sim['Has Smart Thermostats'])
                        st.session_state.has_integrated_security = bool(sim['Has Integrated Security'])
                        st.session_state.has_ev_charging = bool(sim['Has EV Charging'])
                        
                        st.success("Simulation loaded successfully!")
                        st.rerun()
                else:
                    st.info("No saved simulations found in the log.")
            else:
                st.info("No session log file found. Save a simulation first.")
                
        except Exception as e:
            st.error(f"Error loading simulations: {str(e)}")
            st.error("Please check the session log file format.")

    # --- Always use session state for calculations and display ---
    # Recalculate for display if form was not submitted (to show current state)
    annual_rent = st.session_state.monthly_rent * 12
    
    PROPERTY_TAX_RATE = 0.01
    MAINTENANCE_RATE = 0.015
    INSURANCE_RATE = 0.004
    AGENT_FEE_RATE = 0.10

    annual_property_tax_usd = st.session_state.market_price * PROPERTY_TAX_RATE
    annual_maintenance_usd = st.session_state.market_price * MAINTENANCE_RATE
    annual_insurance_usd = st.session_state.market_price * INSURANCE_RATE
    annual_agent_fees_usd = annual_rent * AGENT_FEE_RATE

    total_annual_expenses_usd = annual_property_tax_usd + annual_maintenance_usd + annual_insurance_usd + annual_agent_fees_usd
    net_annual_income_usd = annual_rent - total_annual_expenses_usd

    roi = (net_annual_income_usd / st.session_state.market_price) * 100 if st.session_state.market_price > 0 else 0

    monthly_savings_total = (
        (SOLAR_SAVINGS if st.session_state.has_solar else 0)
        + (WATER_RECYCLING_SAVINGS if st.session_state.has_water_recycling else 0)
        + (SMART_LOCKS_SAVINGS if st.session_state.has_smart_locks else 0)
        + (SMART_THERMOSTATS_SAVINGS if st.session_state.has_smart_thermostats else 0)
        + (INTEGRATED_SECURITY_SAVINGS if st.session_state.has_integrated_security else 0)
        + (EV_CHARGING_SAVINGS if st.session_state.has_ev_charging else 0)
    )
    annual_savings_total = monthly_savings_total * 12

    net_annual_income_with_smart_savings = (annual_rent + annual_savings_total) - total_annual_expenses_usd
    smart_roi = (net_annual_income_with_smart_savings / st.session_state.market_price) * 100 if st.session_state.market_price > 0 else 0

    # Prepare features for model prediction (for display if form not submitted)
    input_data = {
        "stand_size_sqm": stand_size_sqm,
        "building_size_sqm": building_size_sqm,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sale_price_usd": market_price,
        "has_solar": int(has_solar),
        "has_water_recycling": int(has_water_recycling),
        "has_smart_locks": int(has_smart_locks),
        "has_smart_thermostats": int(has_smart_thermostats),
        "has_integrated_security": int(has_integrated_security),
        "has_ev_charging": int(has_ev_charging),
        "location_suburb": location_suburb,
        "property_type": property_type
    }

    input_df = pd.DataFrame([input_data])
    encoded_input_df = pd.get_dummies(input_df, columns=["location_suburb", "property_type"], drop_first=True)

    final_input_df = pd.DataFrame(columns=model_features) 
    for col in model_features:
        if col in encoded_input_df.columns:
            final_input_df[col] = encoded_input_df[col]
        else:
            final_input_df[col] = 0 
    
    for col in ["stand_size_sqm", "building_size_sqm", "bedrooms", "bathrooms", "sale_price_usd"]:
        final_input_df[col] = pd.to_numeric(final_input_df[col])

    predicted_roi_transformed = model.predict(final_input_df)[0]
    predicted_roi_original = pt.inverse_transform(predicted_roi_transformed.reshape(-1, 1)).flatten()[0]

    # --- ROI Calculation ---
    roi = (net_annual_income_usd / market_price) * 100 if market_price > 0 else 0
    smart_roi = (net_annual_income_with_smart_savings / market_price) * 100 if market_price > 0 else 0
    
    # Store ROI values in session state
    st.session_state.roi = float(roi) if roi is not None else 0.0
    st.session_state.smart_roi = float(smart_roi) if smart_roi is not None else 0.0
    st.session_state.predicted_roi_original = float(predicted_roi_original) if 'predicted_roi_original' in locals() else 0.0
    st.session_state.annual_savings_total = float(annual_savings_total) if 'annual_savings_total' in locals() else 0.0

    st.subheader("📊 ROI Results")
    col1, col2, col3 = st.columns(3)
    
    # Get ROI values from session state with fallback to 0.0
    roi_display = st.session_state.get('roi', 0.0)
    smart_roi_display = st.session_state.get('smart_roi', 0.0)
    predicted_roi_display = st.session_state.get('predicted_roi_original', 0.0)
    
    # Display the metrics
    col1.metric("Traditional ROI (Net)", f"{float(roi_display):.2f} %")
    col2.metric("Smart ROI (Net)", f"{float(smart_roi_display):.2f} %")
    col3.metric("Predicted ROI (Model)", f"{float(predicted_roi_display):.2f} %")

    st.markdown("### 💸 Estimated Annual & Lifetime Savings")
    st.write(f"**Annual Savings from Smart Features:** ${annual_savings_total:.2f}")
    st.write(f"**Lifetime Savings (5 Years):** ${annual_savings_total * 5:.2f}")
    st.write(f"**Lifetime Savings (10 Years):** ${annual_savings_total * 10:.2f}")

    # --- Visual Recap ---
    st.subheader("📊 Performance Overview")
    st.caption("This chart compares the estimated ROI under different scenarios based on your latest simulation.")

    # Always create the ROI bar chart for the executive summary
    roi_df = pd.DataFrame({
        "ROI Type": ["Traditional ROI (Net)", "Smart ROI (Net)", "Predicted ROI (Model)"],
        "Value": [roi, smart_roi, predicted_roi_original]
    })
    fig_roi, ax_roi = plt.subplots()
    ax_roi.bar(roi_df["ROI Type"], roi_df["Value"], color=["#003366", "#FFC72C", "#4A4A4A"])
    ax_roi.set_ylabel("ROI (%)")
    ax_roi.set_title("ROI Comparison")
    st.pyplot(fig_roi)

    # Save ONLY this chart to the buffer for PDF and downloads
    roi_chart_buf = io.BytesIO()
    fig_roi.savefig(roi_chart_buf, format="png", bbox_inches='tight', dpi=300)
    roi_chart_buf.seek(0)
    # Store a copy of the buffer in session state
    st.session_state.roi_chart_buf = io.BytesIO(roi_chart_buf.getvalue())
    st.session_state.roi_chart_buf.seek(0)

    st.markdown("### 💰 Financial Breakdown")
    st.write(f"**Annual Rental Income:** ${annual_rent:.2f}")
    st.write(f"**Annual Property Tax:** ${annual_property_tax_usd:.2f}")
    st.write(f"**Annual Maintenance:** ${annual_maintenance_usd:.2f}")
    st.write(f"**Annual Insurance:** ${annual_insurance_usd:.2f}")
    st.write(f"**Annual Agent Fees:** ${annual_agent_fees_usd:.2f}")
    st.write(f"**Total Annual Expenses:** ${total_annual_expenses_usd:.2f}")
    st.write(f"**Net Annual Income (before smart savings):** ${net_annual_income_usd:.2f}")
    st.write(f"**Net Annual Income (with smart savings):** ${net_annual_income_with_smart_savings:.2f}")

    st.markdown("### 📈 ROI Impact of Smart Features")
    st.write("The \"Predicted ROI (Model)\" incorporates the impact of all selected features, including smart features, as learned by the machine learning model.")
    st.write("The \"Smart ROI (Net)\" is a calculated ROI that explicitly adds the estimated monthly savings from smart features to the rental income before subtracting expenses.")

    # --- Save snapshot to server log (moved outside if submit_sim to always log current state) ---
    # This part is already handled inside the if submit_sim block to avoid duplicate logging
    # when the page reloads without form submission.

    # --- ROI Sensitivity Analysis ---
    st.markdown("### 🌀 ROI Sensitivity Analysis (What-If Scenarios)")
    st.caption("Adjust the sliders to see how changes in key variables affect ROI.")

    # Define ranges for sensitivity
    rent_range = st.slider("Monthly Rent Range (USD)", 0, 5000, (int(st.session_state.monthly_rent * 0.7), int(st.session_state.monthly_rent * 1.3)))
    price_range = st.slider("Market Price Range (USD)", 50000, 2000000, (int(st.session_state.market_price * 0.7), int(st.session_state.market_price * 1.3)))
    
    # Enhanced sliders with visual feedback for smart feature adoption
    st.markdown("### 🚀 Smart Feature Impact on ROI")
    st.caption("Adjust adoption rates to see how each smart feature affects your ROI")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        solar_adopt = st.slider(
            "☀️ Solar Panel Adoption", 
            0, 100, 
            100 if st.session_state.has_solar else 0, 
            step=5,
            help="Adds up to $200/month in energy savings and increases property value"
        )
        
        water_recycling_adopt = st.slider(
            "💧 Water Recycling System", 
            0, 100, 
            100 if st.session_state.has_water_recycling else 0, 
            step=5,
            help="Saves up to 30% on water bills and increases property appeal"
        )
        
        smart_locks_adopt = st.slider(
            "🔑 Smart Locks", 
            0, 100, 
            100 if st.session_state.has_smart_locks else 0, 
            step=5,
            help="Reduces insurance costs and increases rental value"
        )
    
    with col2:
        smart_thermostats_adopt = st.slider(
            "🌡️ Smart Thermostats", 
            0, 100, 
            100 if st.session_state.has_smart_thermostats else 0, 
            step=5,
            help="Saves up to 20% on heating/cooling costs"
        )
        
        integrated_security_adopt = st.slider(
            "🚨 Integrated Security", 
            0, 100, 
            100 if st.session_state.has_integrated_security else 0, 
            step=5,
            help="Reduces insurance costs and increases property value"
        )
        
        ev_charging_adopt = st.slider(
            "🔌 EV Charging", 
            0, 100, 
            100 if st.session_state.has_ev_charging else 0, 
            step=5,
            help="Increases property value and rental income potential"
        )

    base_price = st.session_state.market_price
    base_rent = st.session_state.monthly_rent

    # Enhanced ROI calculation with more impactful smart features
    @st.cache_data(ttl=3600, show_spinner="Calculating ROI...")
    def calc_roi_with_expenses(price, rent, solar_pct, water_recycling_pct, smart_locks_pct, 
                             smart_thermostats_pct, integrated_security_pct, ev_charging_pct):
        """Calculate ROI with optimized performance and caching.
        
        Args:
            price: Property price
            rent: Monthly rent
            solar_pct: Solar adoption percentage (0-100)
            water_recycling_pct: Water recycling adoption percentage (0-100)
            smart_locks_pct: Smart locks adoption percentage (0-100)
            smart_thermostats_pct: Smart thermostats adoption percentage (0-100)
            integrated_security_pct: Integrated security adoption percentage (0-100)
            ev_charging_pct: EV charging adoption percentage (0-100)
            
        Returns:
            dict: Dictionary containing ROI and related calculations
        """
        # Convert percentages to decimals for calculations
        solar_pct = float(solar_pct) / 100.0
        water_recycling_pct = float(water_recycling_pct) / 100.0
        smart_locks_pct = float(smart_locks_pct) / 100.0
        smart_thermostats_pct = float(smart_thermostats_pct) / 100.0
        integrated_security_pct = float(integrated_security_pct) / 100.0
        ev_charging_pct = float(ev_charging_pct) / 100.0
        
        # Base values (cached for performance)
        BASE_SAVINGS = {
            'solar': 1200,  # Annual savings from solar
            'water': 600,   # Annual savings from water recycling
            'locks': 300,   # Annual savings from smart locks
            'thermostat': 400,  # Annual savings from smart thermostats
            'security': 500,    # Annual savings from security
            'ev': 600,      # Annual savings from EV charging
        }
        
        # Calculate annual rental income
        annual_rent = float(rent) * 12
        
        # Calculate total annual savings from smart features
        total_savings = (
            (solar_pct * BASE_SAVINGS['solar']) +
            (water_recycling_pct * BASE_SAVINGS['water']) +
            (smart_locks_pct * BASE_SAVINGS['locks']) +
            (smart_thermostats_pct * BASE_SAVINGS['thermostat']) +
            (integrated_security_pct * BASE_SAVINGS['security']) +
            (ev_charging_pct * BASE_SAVINGS['ev'])
        )
        
        # Calculate total annual income (rent + savings)
        total_annual_income = annual_rent + total_savings
        
        # Calculate expenses (simplified for performance)
        # Using a fixed percentage of rental income for expenses
        expense_ratio = 0.35  # 35% of rent goes to expenses
        annual_expenses = annual_rent * expense_ratio
        
        # Calculate net operating income
        noi = total_annual_income - annual_expenses
        
        # Calculate ROI
        price = float(price)
        roi = (noi / price) * 100 if price > 0 else 0
        
        # Return results as a dictionary
        return {
            'roi': max(0, roi),  # ROI can't be negative
            'annual_rent': annual_rent,
            'annual_savings': total_savings,
            'annual_expenses': annual_expenses,
            'noi': noi,
            'total_annual_income': total_annual_income
        }

        # This code is unreachable due to the return statement above
        pass

    # Enhanced visualization options
    st.markdown("### 📊 Analysis Mode")
    mode = st.radio(
        "Select Analysis Mode",
        ["Full Impact (0%→100%)", "What-If (Current→100%)", "Feature Comparison"],
        index=0,
        help=(
            "• Full Impact: Shows ROI change from 0% to 100% adoption\n"
            "• What-If: Shows ROI change from current to 100% adoption\n"
            "• Feature Comparison: Compares individual feature impacts"
        )
    )
    
    # Add a visual separator
    st.markdown("---")

    # Define the current state of smart features for What-If scenario
    current_solar_pct = 100 if st.session_state.has_solar else 0
    current_water_recycling_pct = 100 if st.session_state.has_water_recycling else 0
    current_smart_locks_pct = 100 if st.session_state.has_smart_locks else 0
    current_smart_thermostats_pct = 100 if st.session_state.has_smart_thermostats else 0
    current_integrated_security_pct = 100 if st.session_state.has_integrated_security else 0
    current_ev_charging_pct = 100 if st.session_state.has_ev_charging else 0

    # Create a cache key based on current inputs
    cache_key = f"{base_price}_{base_rent}_{solar_adopt}_{water_recycling_adopt}_{smart_locks_adopt}_{smart_thermostats_adopt}_{integrated_security_adopt}_{ev_charging_adopt}"

    # Only recalculate if inputs have changed
    if 'last_calculation' not in st.session_state or st.session_state.last_calculation != cache_key:
        # Calculate ROI with current settings
        roi_result = calc_roi_with_expenses(
            base_price, 
            base_rent,
            solar_adopt,
            water_recycling_adopt,
            smart_locks_adopt,
            smart_thermostats_adopt,
            integrated_security_adopt,
            ev_charging_adopt
        )
        # Cache the result
        if 'cached_results' not in st.session_state:
            st.session_state.cached_results = {}
        st.session_state.cached_results[cache_key] = roi_result
        st.session_state.last_calculation = cache_key
    else:
        # Use cached result
        roi_result = st.session_state.cached_results[cache_key]

    if mode == "Full Impact (0%→100%)":
        # Show full range from 0% to 100% for each feature
        sensitivity = {
            "Monthly Rent": [
                calc_roi_with_expenses(base_price, rent_range[0], solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, rent_range[1], solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Market Price": [
                calc_roi_with_expenses(price_range[0], base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(price_range[1], base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Solar Adoption": [
                calc_roi_with_expenses(base_price, base_rent, 0, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, 100, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Water Recycling": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, 0, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, 100, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Smart Locks": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, 0, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, 100, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Smart Thermostats": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, 0, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, 100, integrated_security_adopt, ev_charging_adopt)
            ],
            "Integrated Security": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, 0, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, 100, ev_charging_adopt)
            ],
            "EV Charging": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, 0),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, 100)
            ]
        }
    elif mode == "What-If (Current→100%)":
        # Show impact from current slider position to 100% for each feature
        sensitivity = {
            "Monthly Rent": [
                calc_roi_with_expenses(base_price, rent_range[0], solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, rent_range[1], solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Market Price": [
                calc_roi_with_expenses(price_range[0], base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(price_range[1], base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Solar Adoption": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, 100, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Water Recycling": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, 100, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Smart Locks": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, 100, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt)
            ],
            "Smart Thermostats": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, 100, integrated_security_adopt, ev_charging_adopt)
            ],
            "Integrated Security": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, 100, ev_charging_adopt)
            ],
            "EV Charging": [
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt),
                calc_roi_with_expenses(base_price, base_rent, solar_adopt, water_recycling_adopt, smart_locks_adopt, smart_thermostats_adopt, integrated_security_adopt, 100)
            ]
        }
    else:  # Feature Comparison
        # Calculate base ROI with all features at current slider values
        base_roi = calc_roi_with_expenses(
            base_price, base_rent, 
            solar_adopt, water_recycling_adopt, smart_locks_adopt,
            smart_thermostats_adopt, integrated_security_adopt, ev_charging_adopt
        )
        
        # Calculate ROI with each feature's impact
        sensitivity = {
            "Solar Impact": [
                base_roi - (SOLAR_SAVINGS * 12 / base_price * 100 * (solar_adopt/100) * SMART_FEATURE_MULTIPLIER),
                base_roi
            ],
            "Water Recycling Impact": [
                base_roi - (WATER_RECYCLING_SAVINGS * 12 / base_price * 100 * (water_recycling_adopt/100) * SMART_FEATURE_MULTIPLIER),
                base_roi
            ],
            "Smart Locks Impact": [
                base_roi - (SMART_LOCKS_SAVINGS * 12 / base_price * 100 * (smart_locks_adopt/100) * SMART_FEATURE_MULTIPLIER),
                base_roi
            ],
            "Smart Thermostats Impact": [
                base_roi - (SMART_THERMOSTATS_SAVINGS * 12 / base_price * 100 * (smart_thermostats_adopt/100) * SMART_FEATURE_MULTIPLIER),
                base_roi
            ],
            "Integrated Security Impact": [
                base_roi - (INTEGRATED_SECURITY_SAVINGS * 12 / base_price * 100 * (integrated_security_adopt/100) * SMART_FEATURE_MULTIPLIER),
                base_roi
            ],
            "EV Charging Impact": [
                base_roi - (EV_CHARGING_SAVINGS * 12 / base_price * 100 * (ev_charging_adopt/100) * SMART_FEATURE_MULTIPLIER),
                base_roi
            ]
        }

    labels = []
    impacts = []
    for k, v in sensitivity.items():
        # Ensure we're working with numeric ROI values
        roi_start = v[0]['roi'] if isinstance(v[0], dict) else v[0]
        roi_end = v[1]['roi'] if isinstance(v[1], dict) else v[1]
        delta = abs(roi_end - roi_start)
        labels.append(k)
        impacts.append(delta)

    fig, ax = plt.subplots(figsize=(6, 3))
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, impacts, align='center', color="#FFC72C")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('ROI Impact (%)')
    ax.set_title('ROI Sensitivity (Tornado Chart)')
    st.pyplot(fig)

    # --- Show ROI Impact values below the chart ---
    impact_df = pd.DataFrame({
    "Variable": labels,
    "ROI Impact (%)": [f"{v:.2f}" for v in impacts]
    })
    st.markdown("#### ROI Impact by Variable")
    st.dataframe(impact_df, use_container_width=True)

    # --- Project Selection Dropdown for Auto-Fill ---
    st.markdown("#### 🔽 Select a WestProp Project to Auto-Fill Simulation")
    project_options = [
        f"{row['project']} – {row['property_type']}" for _, row in properties_df.iterrows()
    ]
    
    # Project selection dropdown
    selected_project_option = st.selectbox(
        "Choose a Project & Unit Type (optional):",
        options=["(Manual Entry)"] + project_options,
        index=0,
        help="Select a project/unit to auto-fill price, rent, and features. Or use manual entry.",
        key='project_selector',
        on_change=lambda: st.session_state.update({'project_changed': True})
    )
    
    # Handle project selection changes
    if 'project_changed' not in st.session_state:
        st.session_state.project_changed = False
    
    # If a project is selected and it's a new selection
    if selected_project_option != "(Manual Entry)" and st.session_state.project_changed:
        selected_idx = project_options.index(selected_project_option)
        selected_row = properties_df.iloc[selected_idx]
        
        # Default rents for each property type
        default_rents = {
            "Villa - 4 Bed": 2500,
            "Villa - 5 Bed": 3200,
            "Residential Stand": 0,
            "Serviced Apartment (REIT)": 400,
            "Apartment - Studio": 500,
            "Apartment - 1 Bed": 900,
            "Apartment - 2 Bed": 1400,
            "Apartment - 3 Bed": 2000,
            "Townhouse - Garden": 1800,
            "Townhouse - Manor": 2200,
            "Flat": 800
        }
        
        # Update session state with selected project values
        st.session_state.market_price = selected_row["price"]
        st.session_state.monthly_rent = default_rents.get(selected_row["property_type"], 1000)
        st.session_state.has_solar = "Solar" in (selected_row.get("amenities") or [])
        st.session_state.has_water_recycling = "Water Recycling" in (selected_row.get("amenities") or [])
        st.session_state.has_smart_locks = any(x in (selected_row.get("amenities") or []) for x in ["Smart Locks", "Lock-up Shell"])
        st.session_state.has_smart_thermostats = "Smart Thermostats" in (selected_row.get("amenities") or [])
        st.session_state.has_integrated_security = "Integrated Security" in (selected_row.get("amenities") or [])
        st.session_state.has_ev_charging = "EV Charging" in (selected_row.get("amenities") or [])
        
        # Force form re-render by updating the form key
        st.session_state.form_key += 1
        st.session_state.project_changed = False
        
        # Rerun to apply the changes
        st.rerun()
    elif selected_project_option == "(Manual Entry)" and st.session_state.project_changed:
        # Reset form key when switching to manual entry
        st.session_state.form_key += 1
        st.session_state.project_changed = False
        st.rerun()




elif page == "🗂️ My Simulations":
    st.title("🗂️ My Saved Simulations")
    st.markdown("Review and manage your past ROI simulations.")

    file_path = os.path.join(DATA_DIR, "session_log.csv")
    if os.path.exists(file_path):
        session_df = pd.read_csv(file_path)
        if not session_df.empty:
            # Display the dataframe, showing all columns from the updated log
            st.dataframe(session_df)

            st.subheader("Download Simulations")
            csv_data = session_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="my_simulations.csv",
                mime="text/csv",
            )

            st.subheader("Clear All Simulations")
            if st.button("Clear Data"):
                os.remove(file_path)
                st.success("All simulation data cleared!")
                st.rerun()
        else:
            st.info("No simulations saved yet. Run a simulation on the \'Simulator\' page!")
    else:
        st.info("No simulations saved yet. Run a simulation on the \'Simulator\' page!")

elif page == "📈 Executive Summary":
    st.title("💼 Executive Summary: Smart Real Estate ROI Analysis")
    st.markdown("""
    This Executive Summary provides a high-level overview of the financial benefits and strategic implications
    of investing in smart, sustainable real estate, based on your simulation inputs.
    """)

    # Pull from session state with proper defaults
    market_price = st.session_state.get("market_price", 0.0)
    monthly_rent = st.session_state.get("monthly_rent", 0.0)
    roi = st.session_state.get("roi", 0.0)
    smart_roi = st.session_state.get("smart_roi", 0.0)
    predicted_roi = st.session_state.get("predicted_roi_original", 0.0)
    annual_savings = st.session_state.get("annual_savings_total", 0.0)
    roi_chart_buf = st.session_state.get("roi_chart_buf", None)
    
    # Smart features with defaults
    has_solar = st.session_state.get("has_solar", False)
    has_water_recycling = st.session_state.get("has_water_recycling", False)
    has_smart_locks = st.session_state.get("has_smart_locks", False)
    has_smart_thermostats = st.session_state.get("has_smart_thermostats", False)
    has_integrated_security = st.session_state.get("has_integrated_security", False)
    has_ev_charging = st.session_state.get("has_ev_charging", False)
    
    # Calculate annual_savings_total using the same constants as the Simulator tab
    annual_savings_total = (
        (SOLAR_SAVINGS if has_solar else 0)
        + (WATER_RECYCLING_SAVINGS if has_water_recycling else 0)
        + (SMART_LOCKS_SAVINGS if has_smart_locks else 0)
        + (SMART_THERMOSTATS_SAVINGS if has_smart_thermostats else 0)
        + (INTEGRATED_SECURITY_SAVINGS if has_integrated_security else 0)
        + (EV_CHARGING_SAVINGS if has_ev_charging else 0)
    ) * 12

    # --- Visual Recap ---
    st.subheader("📊 Performance Overview")
    st.caption("This chart compares the estimated ROI under different scenarios based on your latest simulation.")

    # Display the ROI chart generated on the Simulator tab, if available; this keeps charts in sync
    if 'roi_chart_buf' in st.session_state and st.session_state.roi_chart_buf is not None:
        try:
            # Create a new buffer from the session state buffer
            buf = io.BytesIO(st.session_state.roi_chart_buf.getvalue())
            buf.seek(0)
            chart_img = Image.open(buf)
            st.image(chart_img, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not display ROI chart: {str(e)}. Please run a simulation first.")
    else:
        st.warning("Run a simulation in the Simulator tab first to see the ROI comparison chart.")

    # --- Financial Metrics ---
    st.subheader("Financial Impact")
    
    # Calculate 5-year and 10-year savings
    five_year_savings = annual_savings_total * 5
    ten_year_savings = annual_savings_total * 10
    
    # Display metrics in columns for better visual organization
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estimated Annual Savings", f"${annual_savings_total:,.2f}")
    with col2:
        st.metric("5-Year Savings", f"${five_year_savings:,.2f}")
    with col3:
        st.metric("10-Year Savings", f"${ten_year_savings:,.2f}")

    # --- Smart Feature Impact ---
    st.subheader("Smart Feature Impact")
    
    # Create a list of active smart features
    active_features = []
    if has_solar: active_features.append("Solar Panels")
    if has_water_recycling: active_features.append("Water Recycling")
    if has_smart_locks: active_features.append("Smart Locks")
    if has_smart_thermostats: active_features.append("Smart Thermostats")
    if has_integrated_security: active_features.append("Integrated Security")
    if has_ev_charging: active_features.append("EV Charging")
    
    if active_features:
        st.write("Active smart features contributing to your savings:")
        for feature in active_features:
            st.write(f" {feature}")
    else:
        st.info("No smart features are currently active. Enable features above to see potential savings.")

    # Add some interpretation
    if smart_roi > roi:
        st.success(f" Smart features increase your ROI by {smart_roi - roi:.2f} percentage points!")
    else:
        st.info(" Enabling more smart features could potentially increase your ROI.")

    # Store values in session state
    st.session_state.roi = float(roi) if roi is not None else 0.0
    st.session_state.smart_roi = float(smart_roi) if smart_roi is not None else 0.0
    st.session_state.predicted_roi_original = float(predicted_roi) if predicted_roi is not None else 0.0
    st.session_state.annual_savings_total = float(annual_savings_total) if annual_savings_total is not None else 0.0

    # Prepare smart_features_status dictionary for PDF generation
    smart_features_status = {
        "has_solar": has_solar,
        "has_water_recycling": has_water_recycling,
        "has_smart_locks": has_smart_locks,
        "has_smart_thermostats": has_smart_thermostats,
        "has_integrated_security": has_integrated_security,
        "has_ev_charging": has_ev_charging
    }

    # --- Dynamic PDF Generation ---
    def generate_pdf(market_price, monthly_rent, smart_features_status, roi, smart_roi, predicted_roi, annual_savings, roi_chart_buf):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Define layout constants
        MARGIN = 40
        COL1_WIDTH = 240
        COL2_WIDTH = 250
        LINE_HEIGHT = 14
        SECTION_SPACING = 25
        PAGE_WIDTH, PAGE_HEIGHT = A4
        
        # --- Helper Functions ---
        def draw_section_header(text, y):
            c.setFont("Helvetica-Bold", 12)
            c.setFillColorRGB(0.2, 0.4, 0.6)  # Dark blue color for headers
            c.drawString(MARGIN, y, text.upper())
            c.setLineWidth(1.5)
            c.line(MARGIN, y - 3, MARGIN + 100, y - 3)
            c.setFillColorRGB(0, 0, 0)  # Reset to black
            return y - SECTION_SPACING
            
        def draw_metric(label, value, x, y, bold_label=True, value_format='${:,.2f}'):
            if bold_label:
                c.setFont("Helvetica-Bold", 10)
            else:
                c.setFont("Helvetica", 10)
            c.drawString(x, y, f"{label}:")
            
            # Format value based on type
            if isinstance(value, (int, float)):
                if '%' in label.upper():
                    value_str = f"{value:.2f}%"
                else:
                    value_str = value_format.format(value)
            else:
                value_str = str(value)
                
            c.setFont("Helvetica", 10)
            c.drawRightString(x + 200, y, value_str)
            return y - 18
        
        def draw_text_box(text, x, y, width, height, title=None, font_size=10, line_height=12):
            # Draw box
            c.rect(x, y - height, width, height)
            
            # Add title if provided
            if title:
                c.setFont("Helvetica-Bold", font_size)
                c.drawString(x + 5, y - 15, title)
                y -= 20
                c.line(x, y, x + width, y)
                y -= 5
            
            # Add text with wrapping
            c.setFont("Helvetica", font_size)
            text_object = c.beginText(x + 5, y - 5)
            
            # Simple text wrapping
            words = text.split()
            line = []
            for word in words:
                test_line = ' '.join(line + [word])
                if c.stringWidth(test_line, "Helvetica", font_size) < (width - 10):
                    line.append(word)
                else:
                    text_object.textLine(' '.join(line))
                    line = [word]
            if line:
                text_object.textLine(' '.join(line))
            
            c.drawText(text_object)
            return y - height - 10
        
        # --- Page 1: Summary ---
        # Header with logo and title
        try:
            c.drawImage("westprop_logo.png", MARGIN, 770, width=100, preserveAspectRatio=True, mask='auto')
        except:
            pass
            
        # Main title
        c.setFont("Helvetica-Bold", 18)
        c.setFillColorRGB(0.2, 0.4, 0.6)  # Dark blue
        c.drawString(MARGIN, 800, "WESTPROP")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(MARGIN, 775, "SMART REAL ESTATE ANALYSIS")
        
        # Date and page info
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray
        c.drawString(MARGIN, 760, f"Generated: {dt.now().strftime('%B %d, %Y')}")
        c.drawRightString(PAGE_WIDTH - MARGIN, 760, "Page 1 of 2")
        c.setFillColorRGB(0, 0, 0)  # Reset to black
        
        # Divider line
        c.line(MARGIN, 755, PAGE_WIDTH - MARGIN, 755)
        
        # --- Section 1: Key Metrics ---
        y_position = 730
        y_position = draw_section_header("Key Investment Metrics", y_position)
        
        # Left column - Financials
        x_left = MARGIN
        y_position = draw_metric("Market Price", market_price, x_left, y_position)
        y_position = draw_metric("Monthly Rental Income", monthly_rent, x_left, y_position)
        y_position = draw_metric("Annual Savings", annual_savings, x_left, y_position)
        
        # Right column - ROI Metrics
        x_right = MARGIN + COL1_WIDTH + 20
        y_right = 730 - SECTION_SPACING
        y_right = draw_metric("Traditional ROI", roi, x_right, y_right, value_format='{:.2f}%')
        y_right = draw_metric("Smart ROI", smart_roi, x_right, y_right, value_format='{:.2f}%')
        y_right = draw_metric("Predicted ROI", predicted_roi, x_right, y_right, value_format='{:.2f}%')
        
        # ROI Chart
        if roi_chart_buf is not None:
            try:
                roi_chart_buf.seek(0)
                img = ImageReader(roi_chart_buf)
                chart_width = 400
                chart_height = 200
                chart_x = (PAGE_WIDTH - chart_width) / 2  # Center the chart
                c.drawImage(img, chart_x, y_position - chart_height - 20, width=chart_width, height=chart_height, preserveAspectRatio=True, mask='auto')
                y_position -= chart_height + 40
            except Exception as e:
                print(f"Error drawing ROI chart: {e}")
        
        # --- Section 2: Smart Features ---
        y_position = draw_section_header("Smart Features", y_position)
        
        # Create list of active features
        features = []
        if smart_features_status.get('has_solar', False): features.append("✓ Solar Panels")
        if smart_features_status.get('has_water_recycling', False): features.append("✓ Water Recycling")
        if smart_features_status.get('has_smart_locks', False): features.append("✓ Smart Locks")
        if smart_features_status.get('has_smart_thermostats', False): features.append("✓ Smart Thermostats")
        if smart_features_status.get('has_integrated_security', False): features.append("✓ Integrated Security")
        if smart_features_status.get('has_ev_charging', False): features.append("✓ EV Charging")
        
        if not features:
            features = ["No smart features enabled"]
        
        # Draw features in 3 columns
        col_height = (len(features) + 2) // 3  # Distribute features in 3 columns
        col_width = (PAGE_WIDTH - 2 * MARGIN) / 3 - 10
        
        for i, feature in enumerate(features):
            col = i // col_height
            row = i % col_height
            x = MARGIN + col * (col_width + 10)
            y = y_position - (row * 18)
            c.drawString(x, y, feature)
        
        y_position -= (col_height * 18) + 20
        
        # --- Section 3: Financial Projections ---
        y_position = draw_section_header("Financial Projections", y_position)
        
        # Left column - Savings
        y_savings = y_position
        y_savings = draw_metric("5-Year Savings", annual_savings * 5, MARGIN, y_savings)
        y_savings = draw_metric("10-Year Savings", annual_savings * 10, MARGIN, y_savings)
        
        # Right column - Additional metrics
        y_metrics = y_position
        y_metrics = draw_metric("Monthly Cash Flow", monthly_rent * 0.8, MARGIN + COL1_WIDTH + 20, y_metrics)  # Example metric
        y_metrics = draw_metric("Cap Rate", smart_roi * 0.8, MARGIN + COL1_WIDTH + 20, y_metrics, value_format='{:.2f}%')  # Example metric
        
        y_position = min(y_savings, y_metrics) - 20
        
        # --- Section 4: Analysis ---
        y_position = draw_section_header("Investment Analysis", y_position)
        
        analysis_text = """This analysis highlights the financial benefits of smart home features in your real estate investment. 
        The enhanced ROI is achieved through multiple value drivers that contribute to both income growth and expense reduction.
        
        Key Benefits:
        • Energy Efficiency: Smart thermostats and solar panels reduce utility costs
        • Higher Rental Premium: Tech-savvy tenants pay more for smart features
        • Lower Vacancy: Smart homes attract and retain quality tenants
        • Increased Property Value: Smart features boost resale value
        • Tax Benefits: Potential deductions for energy-efficient upgrades
        
        Recommendation: Implementing the suggested smart features can significantly enhance your investment returns. 
        The projected ROI of {:.2f}% demonstrates strong potential for value creation.""".format(smart_roi)
        
        # Draw text box with analysis
        y_position = draw_text_box(
            analysis_text, 
            MARGIN, 
            y_position, 
            PAGE_WIDTH - 2 * MARGIN, 
            180,
            "Investment Insights",
            font_size=9,
            line_height=11
        )
        
        # Footer
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray
        c.drawString(MARGIN, 30, "*This is an auto-generated summary using real-time inputs. All values are estimates and should be verified by a financial advisor.*")
        
        # --- Page 2: Additional Details ---
        c.showPage()
        
        # Page 2 Header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(MARGIN, 800, "DETAILED ANALYSIS & METHODOLOGY")
        c.setFont("Helvetica", 8)
        c.drawRightString(PAGE_WIDTH - MARGIN, 800, "Page 2 of 2")
        c.line(MARGIN, 795, PAGE_WIDTH - MARGIN, 795)
        
        # Methodology Section
        y_position = 770
        y_position = draw_section_header("Methodology", y_position)
        
        methodology_text = """This analysis is based on the following assumptions and calculations:
        
        1. Traditional ROI: (Annual Rental Income - Operating Expenses) / Property Price
        2. Smart ROI: Adjusts for increased rental income and reduced operating expenses from smart features
        3. Predicted ROI: Machine learning model based on historical data from similar properties
        4. Annual Savings: Estimated from utility savings, insurance discounts, and maintenance reductions
        
        The analysis assumes a 5-year holding period and accounts for:
        • 2% annual rent increase
        • 2.5% annual operating expense growth
        • 3% annual property appreciation
        • 5% vacancy rate
        • 8% property management fees"""
        
        y_position = draw_text_box(
            methodology_text,
            MARGIN,
            y_position,
            PAGE_WIDTH - 2 * MARGIN,
            200,
            "Calculation Methodology",
            font_size=9,
            line_height=11
        )
        
        # Next Steps Section
        y_position = draw_section_header("Next Steps", y_position)
        
        next_steps = """1. Schedule a consultation with our real estate investment team
        2. Tour available properties with smart features
        3. Review financing options and tax benefits
        4. Finalize investment strategy and timeline
        
        Contact our team today to discuss how we can help you maximize your real estate investment returns."""
        
        y_position = draw_text_box(
            next_steps,
            MARGIN,
            y_position,
            PAGE_WIDTH - 2 * MARGIN,
            120,
            "Your Next Steps",
            font_size=9,
            line_height=11
        )
        
        # Finalize PDF
        c.save()
        buffer.seek(0)
        return buffer

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # Get ROI values from session state to ensure we have the latest values
    roi = st.session_state.get('roi', 0.0)
    smart_roi = st.session_state.get('smart_roi', 0.0)
    predicted_roi = st.session_state.get('predicted_roi_original', 0.0)
    
    # Generate the PDF data before using it
    pdf_data = generate_pdf(
        market_price,
        monthly_rent,
        smart_features_status,
        float(roi),  # Ensure these are float values
        float(smart_roi),
        float(predicted_roi),
        float(annual_savings_total),
        st.session_state.get('roi_chart_buf')
    )

    st.download_button(
        label=" Download Full One-Pager PDF",
        data=pdf_data,
        file_name="WestProp_Smart_ROI_Summary.pdf",
        mime="application/pdf",
        key="download_pdf_1"
    )

    # --- CSV Download ---
    summary_df = pd.DataFrame({
        "Metric": ["Traditional ROI", "Smart ROI", "Predicted ROI", "Annual Savings", "5Y Savings", "10Y Savings"],
        "Value": [roi, smart_roi, predicted_roi, annual_savings, annual_savings * 5, annual_savings * 10]
    })
    csv = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📊 Download ROI Summary (CSV)",
        data=csv,
        file_name="roi_summary.csv",
        mime="text/csv",
        key="download_csv_1"
    )

    # --- EMAIL SUMMARY FEATURE (ONLY IN EXECUTIVE SUMMARY TAB) ---
    st.markdown("### 📧 Email Your Executive Summary")
    email_address = st.text_input(
        "Enter your email address to receive the summary (PDF & CSV):",
        key="exec_summary_email_1"
    )
    if st.button("Send Summary to Email"):
        if email_address:
            with st.spinner("Preparing and sending your executive summary..."):
                try:
                    # --- Prepare PDF and CSV ---
                    pdf_data.seek(0)
                    csv_data = summary_df.to_csv(index=False).encode("utf-8")

                    # --- Compose Email ---
                    msg = EmailMessage()
                    msg["Subject"] = "Your WestProp Smart ROI Executive Summary"
                    msg["From"] = SENDER_EMAIL
                    msg["To"] = email_address
                    msg.set_content(
                        "Attached is your Smart ROI Executive Summary from WestProp.\n\n"
                        "Thank you for using our dashboard!"
                    )
                    msg.add_attachment(pdf_data.read(), maintype="application", subtype="pdf", filename="WestProp_Smart_ROI_Summary.pdf")
                    msg.add_attachment(csv_data, maintype="text", subtype="csv", filename="roi_summary.csv")

                    # --- Send Email (Gmail SMTP example) ---
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                        smtp.login(SENDER_EMAIL, APP_PASSWORD)
                        smtp.send_message(msg)
                    
                    st.success("✅ Summary sent to your email!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")
                    st.error("Please check your internet connection and try again.")
        else:
            st.warning("⚠️ Please enter a valid email address.")

# --- MAP VIEW ---
@st.cache_data(ttl=3600)
def load_map_data():
    try:
        # Load and preprocess map data
        df = pd.read_csv("westprop_streamlit_dataset.csv")
        
        # Convert ROI to numeric, handling any non-numeric values
        if 'ROI (%)' in df.columns:
            df['ROI (%)'] = pd.to_numeric(df['ROI (%)'], errors='coerce')
            
        # Ensure required columns exist, add if missing with default values
        required_columns = ['Project', 'Latitude', 'Longitude', 'ROI (%)']
        for col in required_columns:
            if col not in df.columns:
                if col == 'ROI (%)':
                    df[col] = 0.0  # Default ROI if missing
                else:
                    df[col] = ''  # Empty string for other missing columns
        
        # Drop any rows with missing coordinates or project names
        df = df.dropna(subset=['Project', 'Latitude', 'Longitude'])
        
        return df
        
    except Exception as e:
        st.error(f"Error loading map data: {str(e)}")
        # Return a minimal valid dataframe if there's an error
        return pd.DataFrame({
            'Project': ['Sample Project'],
            'Latitude': [-17.8],
            'Longitude': [31.0],
            'ROI (%)': [0.0]
        })

if page == "🗺️ ROI Map":
    st.title("🗺️ Interactive ROI Map with Heatmap View")
    
    # Add loading state for better UX
    with st.spinner("Loading map data..."):
        df = load_map_data()
    
    st.sidebar.markdown("---")
    min_roi = st.sidebar.slider("Minimum ROI to display (%)", 0.0, 20.0, 9.0, step=0.1)
    
    # Cache the filtered data
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_filtered_data(_df, min_roi):
        return _df[_df["ROI (%)"] >= min_roi].copy()
    
    filtered_df = get_filtered_data(df, min_roi)
    show_heatmap = st.sidebar.checkbox("Show Heatmap Layer", value=True)
    show_markers = st.sidebar.checkbox("Show ROI Markers", value=True)

    # Load data safely with explicit path
    try:
        df = pd.read_csv("data/westprop_streamlit_dataset.csv")
        # Ensure required columns exist and have proper data types
        required_columns = ["Project", "Latitude", "Longitude", "ROI (%)"]
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Error: Required column '{col}' not found in the dataset.")
                st.stop()
        
        # Convert numeric columns to appropriate types
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors='coerce')
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors='coerce')
        df["ROI (%)"] = pd.to_numeric(df["ROI (%)"], errors='coerce')
        
        # Drop rows with missing coordinates or ROI
        df = df.dropna(subset=["Latitude", "Longitude", "ROI (%)"])
        
        if df.empty:
            st.error("Error: No valid data found in the dataset after cleaning.")
            st.stop()
            
    except FileNotFoundError:
        st.error("Error: data/westprop_streamlit_dataset.csv not found. Please ensure the file exists in the data/ directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

    # Define the match_project_name function inside the ROI Map tab
    def match_project_name(lat_clicked, lon_clicked, dataset, threshold=0.0005):
        for _, row in dataset.iterrows():
            if abs(row["Latitude"] - lat_clicked) <= threshold and abs(row["Longitude"] - lon_clicked) <= threshold:
                return row["Project"]
        return "Unknown Location"

    # Filter data based on minimum ROI
    filtered_df = df[df["ROI (%)"] >= min_roi].copy()
    
    # Cache the map creation
    @st.cache_data(ttl=300, hash_funcs={folium.Map: id})
    def create_base_map():
        return folium.Map(
            location=[-17.8, 31.0],  # Default to Harare
            zoom_start=12,
            tiles="cartodbpositron",
            control_scale=True,
            prefer_canvas=True,  # Better performance with many markers
            min_zoom=10,
            max_zoom=18
        )
    
    m = create_base_map()

    if show_markers and not filtered_df.empty:
        # Add markers with clustering for better performance
        from folium.plugins import MarkerCluster
        
        # Create a marker cluster
        marker_cluster = MarkerCluster(
            name="Properties",
            overlay=True,
            control=True,
            icon_create_function=None
        ).add_to(m)
        
        # Add markers to the cluster
        for idx, row in filtered_df.iterrows():
            # Create popup with available data
            popup_content = f"<b>{row['Project']}</b><br>"
            popup_content += f"ROI: {row['ROI (%)']:.1f}%<br>"
            
            # Only add type if the column exists
            if 'Project Type' in row and pd.notna(row['Project Type']):
                popup_content += f"Type: {row['Project Type']}"
                
            popup = folium.Popup(popup_content, max_width=250)
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=popup,
                tooltip=row['Project'],
                icon=folium.Icon(color='blue', icon='home')
            ).add_to(marker_cluster)

    if show_heatmap and not filtered_df.empty:
        # Only include valid coordinates in heatmap
        heat_data = [
            [row["Latitude"], row["Longitude"], row["ROI (%)"]] 
            for _, row in filtered_df.iterrows() 
            if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"])
        ]
        if heat_data:  # Only add heatmap if we have valid data points
            HeatMap(heat_data, radius=25).add_to(m)

    # Display the map with optimized rendering and capture interactions
    map_interaction = st_folium(
        m,
        width='100%',
        height=600,
        use_container_width=True,
        returned_objects=["last_clicked", "bounds", "zoom"],
        zoom=12,
        center=[-17.8, 31.0],
        key="map"
    )
    
    # Initialize simulation data in session state if not exists
    if 'simulation_data' not in st.session_state:
        st.session_state.simulation_data = {
            'clicked': False
        }
    
    # Handle map clicks and ROI simulation
    if map_interaction and map_interaction.get("last_clicked"):
        lat = map_interaction["last_clicked"]["lat"]
        lon = map_interaction["last_clicked"]["lng"]

        # Store the click data in session state
        st.session_state.last_click = {
            'lat': lat,
            'lon': lon,
            'clicked': True
        }

        # Match to project name with a larger threshold
        matched_project = match_project_name(lat, lon, df)
        
        # Find the nearest project within a reasonable distance
        nearest_project = None
        if lat is not None and lon is not None:
            df['distance'] = ((df['Latitude'] - lat) ** 2 + (df['Longitude'] - lon) ** 2) ** 0.5
            nearest_project = df.sort_values('distance').iloc[0] if not df.empty else None
        
        # Handle ROI calculation if we have a valid nearest project
        max_distance = 0.02  # ~2km at the equator
        
        # Initialize default values
        base_roi = 5.0  # Default base ROI for undeveloped areas
        simulated_roi = max(0.1, base_roi + (random.random() * 4 - 2))  # Random value between base_roi±2%
        project_name = "Undeveloped Area"
        distance = None
        distance_km = 0
        
        # Check if nearest_project exists and has required attributes
        if (nearest_project is not None and 
            'distance' in nearest_project and 
            'ROI (%)' in nearest_project and 
            'Project' in nearest_project):
            
            distance = nearest_project['distance']
            
            if distance < max_distance:
                # If close to a project, use its ROI with slight distance-based adjustment
                base_roi = nearest_project['ROI (%)']
                # Reduce ROI slightly based on distance (further = lower ROI)
                distance_factor = 1 - (distance / max_distance) * 0.3  # Up to 30% reduction
                simulated_roi = max(0.1, base_roi * distance_factor)
                project_name = nearest_project['Project']
        
        # Calculate distance in kilometers if available
        distance_km = distance * 111 if distance is not None else 0
        is_developed = project_name != "Undeveloped Area"
        
        # Update session state with simulation data
        st.session_state.simulation_data = {
            'is_developed': is_developed,
            'project_name': project_name,
            'distance_km': distance_km,
            'base_roi': base_roi,
            'simulated_roi': simulated_roi,
            'clicked': True
        }
    
    # Only show ROI information if the user has clicked on the map
    if st.session_state.simulation_data.get('clicked', False):
        project_name = st.session_state.simulation_data['project_name']
        is_developed = st.session_state.simulation_data['is_developed']
        simulated_roi = st.session_state.simulation_data['simulated_roi']
        base_roi = st.session_state.simulation_data['base_roi']
        distance_km = st.session_state.simulation_data.get('distance_km', 0)
        
        # Display information to the user
        st.markdown(f"📍 **You clicked near:** `{project_name}`")
        if is_developed and distance_km > 0:
            st.markdown(f"📏 **Distance from project center:** ~{distance_km:.2f} km")
            st.markdown(f"📈 **Estimated ROI:** {simulated_roi:.2f}% (Base: {base_roi:.2f}%)")
        else:
            st.markdown(f"📊 **Estimated ROI for undeveloped area:** {simulated_roi:.2f}%")
        
        st.markdown(f"🏢 **Nearest Project:** `{project_name if project_name != 'Unknown Location' else 'No nearby projects'}`")
        st.markdown(f"💡 **Estimated ROI at this location:** `{simulated_roi:.2f}%")

        # Voting section
        st.subheader("🗳️ Would You Invest In This Location?")
        vote = st.radio("Your Vote", ["Yes", "No"], horizontal=True, 
                       help="Would you consider investing in a property at this location?",
                       key="vote_radio_main")

        if st.button("Submit Vote", key="submit_vote_main"):
            try:
                # Create new vote record
                new_vote = pd.DataFrame([{
                    "Project": project_name,
                    "Latitude": lat,
                    "Longitude": lon,
                    "ROI (%)": round(simulated_roi, 2),
                    "Vote": vote,
                    "Timestamp": dt.now().isoformat()
                }])
                
                # Try to read existing votes
                try:
                    existing_votes = pd.read_csv("vote_results.csv")
                    vote_data = pd.concat([existing_votes, new_vote], ignore_index=True)
                except FileNotFoundError:
                    vote_data = new_vote
                
                # Save to CSV
                vote_data.to_csv("vote_results.csv", index=False)
                st.success("✅ Your vote has been recorded for this project!")
                
            except Exception as e:
                st.error(f"❌ Error recording vote: {str(e)}")

        # This section was removed to prevent duplicate voting UI
    
    # Voting admin login section
    if "voting_admin_logged_in" not in st.session_state:
        st.session_state.voting_admin_logged_in = False

    if not st.session_state.voting_admin_logged_in:
        with st.form("voting_admin_login_form"):
            st.subheader("Voting Admin Login")
            password_input = st.text_input("Enter voting admin password:", type="password")
            if st.form_submit_button("Login as Voting Admin"):
                if password_input == "westprop2025":
                    st.session_state.voting_admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")


    if st.session_state.get("voting_admin_logged_in", False):
        st.subheader("🔒 Admin Panel — Voting Data")
        
        # Load votes data
        try:
            recent_votes = pd.read_csv("vote_results.csv")
            if recent_votes.empty:
                st.warning("No votes recorded yet.")
            else:
                st.dataframe(recent_votes.tail(10))
                
                # Display voting statistics
                st.subheader("📊 Voting Statistics")
                
                # Calculate overall vote distribution
                vote_counts = recent_votes['Vote'].value_counts()
                
                # Tab layout for different views
                tab1, tab2 = st.tabs(["Overall Results", "By Location"])
                
                with tab1:
                    # Overall vote distribution
                    st.markdown("### Overall Vote Distribution")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Create bar chart for overall votes
                        fig1, ax1 = plt.subplots(figsize=(8, 4))
                        vote_counts.plot(kind='bar', color=['#4CAF50', '#F44336'], ax=ax1)
                        ax1.set_title('Vote Distribution (Overall)')
                        ax1.set_xlabel('Vote')
                        ax1.set_ylabel('Number of Votes')
                        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
                        
                        # Add count labels on top of bars
                        for i, v in enumerate(vote_counts):
                            ax1.text(i, v + 0.2, str(v), ha='center', va='bottom')
                        
                        st.pyplot(fig1)
                    
                    with col2:
                        # Display summary statistics
                        st.metric("Total Votes", len(recent_votes))
                        if 'Yes' in vote_counts:
                            st.metric("👍 Yes Votes", f"{vote_counts['Yes']} ({(vote_counts['Yes']/len(recent_votes)*100):.1f}%)")
                        if 'No' in vote_counts:
                            st.metric("👎 No Votes", f"{vote_counts['No']} ({(vote_counts['No']/len(recent_votes)*100):.1f}%)")
                
                with tab2:
                    # Location-based analysis
                    st.markdown("### 🗺️ Votes by Location")
                    
                    # Group by Project and Vote
                    if 'Project' in recent_votes.columns and not recent_votes.empty:
                        # Calculate votes by location
                        location_votes = recent_votes.groupby(['Project', 'Vote']).size().unstack(fill_value=0)
                        
                        # Add any missing vote columns
                        for vote in ['Yes', 'No']:
                            if vote not in location_votes.columns:
                                location_votes[vote] = 0
                        
                        # Calculate totals and percentages
                        location_votes['Total'] = location_votes.sum(axis=1)
                        location_votes = location_votes.sort_values('Total', ascending=False)
                        
                        # Create a figure with subplots
                        fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(12, 12), 
                                                      gridspec_kw={'height_ratios': [3, 1]},
                                                      facecolor='#f8f9fa')
                        
                        # Set style
                        plt.style.use('ggplot')
                        
                        # Plot location-based results with better formatting
                        bars = location_votes[['Yes', 'No']].plot(
                            kind='barh',  # Horizontal bars for better project name display
                            stacked=True,
                            color=['#4CAF50', '#F44336'],
                            ax=ax2,
                            width=0.7,  # Slightly thinner bars
                            edgecolor='white',
                            linewidth=0.7
                        )
                        
                        # Customize the chart
                        ax2.set_title('Votes by Project', fontsize=14, pad=20, fontweight='bold')
                        ax2.set_xlabel('Number of Votes', fontsize=12, labelpad=10)
                        ax2.set_ylabel('Project', fontsize=12, labelpad=10)
                        ax2.legend(title='Vote', bbox_to_anchor=(1.02, 1), loc='upper left')
                        ax2.grid(axis='x', linestyle='--', alpha=0.7)
                        
                        # Add value and percentage labels on the bars
                        for i, (idx, row) in enumerate(location_votes.iterrows()):
                            total = row['Total']
                            y_pos = i  # Current y-position for the bar segment
                            
                            # Add Yes votes label
                            if row.get('Yes', 0) > 0:
                                yes_pct = (row['Yes'] / total) * 100
                                ax2.text(
                                    row['Yes']/2, y_pos,
                                    f"{row['Yes']} ({yes_pct:.1f}%)",
                                    ha='center', va='center',
                                    color='white', fontweight='bold',
                                    fontsize=9
                                )
                            
                            # Add No votes label
                            if row.get('No', 0) > 0:
                                no_pct = (row['No'] / total) * 100
                                ax2.text(
                                    row['Yes'] + row['No']/2, y_pos,
                                    f"{row['No']} ({no_pct:.1f}%)",
                                    ha='center', va='center',
                                    color='white', fontweight='bold',
                                    fontsize=9
                                )
                        
                        # Create a donut chart for overall distribution
                        wedges, texts, autotexts = ax3.pie(
                            vote_counts,
                            labels=vote_counts.index,
                            autopct='%1.1f%%',
                            colors=['#4CAF50', '#F44336'],
                            startangle=90,
                            wedgeprops=dict(width=0.4),  # Create donut chart
                            textprops={'fontsize': 10}
                        )
                        
                        # Style the donut chart
                        centre_circle = plt.Circle((0,0), 0.6, fc='white')
                        ax3.add_artist(centre_circle)
                        ax3.set_title('Overall Vote Distribution', fontsize=12, pad=20, fontweight='bold')
                        ax3.axis('equal')
                        
                        # Add total votes in the center of the donut
                        total_votes = vote_counts.sum()
                        ax3.text(0, 0, f"Total\n{total_votes} votes", 
                                ha='center', va='center', 
                                fontsize=12, fontweight='bold')
                        
                        # Adjust layout and display
                        plt.tight_layout()
                        plt.subplots_adjust(hspace=0.4)  # Add some space between subplots
                        st.pyplot(fig2)
                        
                        # Show detailed breakdown in an expandable section
                        with st.expander("📊 View Detailed Vote Breakdown"):
                            # Calculate percentages for the table
                            display_df = location_votes.copy()
                            display_df['Yes %'] = (display_df['Yes'] / display_df['Total'] * 100).round(1)
                            display_df['No %'] = (display_df['No'] / display_df['Total'] * 100).round(1)
                            
                            # Reorder columns for better readability
                            display_df = display_df[['Total', 'Yes', 'Yes %', 'No', 'No %']]
                            
                            # Style the dataframe
                            styled_df = display_df.style\
                                .background_gradient(subset=['Yes %', 'No %'], cmap='YlGn')\
                                .format({
                                    'Yes %': '{:.1f}%',
                                    'No %': '{:.1f}%',
                                    'Total': '{:,.0f}'
                                })
                            
                            st.dataframe(styled_df)
                    else:
                        st.warning("No location data available in the voting records.")
                
                st.markdown("---")
                
                # Reset Votes Section
                st.subheader("⚠️ Reset All Votes")
                st.warning("This action will permanently delete all voting records and cannot be undone.")
                
                # Confirmation dialog for reset
                if st.checkbox("I understand this action cannot be undone"):
                    if st.button("🔴 Reset All Votes", 
                              help="Permanently delete all voting records",
                              type="primary"):
                        try:
                            # Delete the vote results file
                            if os.path.exists("vote_results.csv"):
                                os.remove("vote_results.csv")
                                st.success("All votes have been successfully reset.")
                                st.rerun()
                            else:
                                st.warning("No vote records found to delete.")
                        except Exception as e:
                            st.error(f"Error resetting votes: {str(e)}")
                
                st.markdown("---")
                st.subheader("Export Data")
                
                # Add export buttons in a single row
                col1, col2 = st.columns(2)
                with col1:
                    # CSV Download
                    csv = recent_votes.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "💾 Download Votes (CSV)",
                        data=csv,
                        file_name="westprop_vote_results.csv",
                        mime="text/csv",
                        help="Download all voting data as a CSV file"
                    )
                
                with col2:
                    # Email Export
                    with st.form("email_vote_report_form"):
                        email = st.text_input("Recipient Email", "admin@westprop.com")
                        submit_button = st.form_submit_button("📧 Send Report")
                        
                        if submit_button:
                            # Create a status container for the spinner and messages
                            status_container = st.empty()
                            with status_container:
                                with st.spinner("📤 Preparing and sending report..."):
                                    try:
                                        from email_service import send_email
                                        import tempfile
                                        import os
                                        import matplotlib.pyplot as plt
                                        
                                        # Generate vote statistics
                                        total_votes = len(recent_votes)
                                        yes_votes = len(recent_votes[recent_votes['Vote'] == 'Yes'])
                                        no_votes = len(recent_votes[recent_votes['Vote'] == 'No'])
                                        yes_pct = (yes_votes / total_votes * 100) if total_votes > 0 else 0
                                        
                                        # Group by project
                                        project_votes = recent_votes.groupby('Project')['Vote'].value_counts().unstack(fill_value=0)
                                        project_votes['Total'] = project_votes.get('Yes', 0) + project_votes.get('No', 0)
                                        project_votes['Yes %'] = (project_votes.get('Yes', 0) / project_votes['Total'] * 100).round(1)
                                        
                                        # Create email content
                                        subject = f"WestProp Voting Report - {dt.now().strftime('%Y-%m-%d')}"
                                        
                                        # Create styled HTML for project votes table
                                        styled_project_votes = project_votes.style\
                                            .set_table_attributes('class="dataframe" style="border-collapse: collapse; width: 100%;"')\
                                            .set_properties(**{'text-align': 'center', 'border': '1px solid #ddd'})\
                                            .set_table_styles([
                                                {'selector': 'th', 'props': [('background-color', '#f2f2f2'), 
                                                                          ('padding', '12px'),
                                                                          ('text-align', 'center'),
                                                                          ('border-bottom', '1px solid #ddd')]},
                                                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
                                                {'selector': 'tr:hover', 'props': [('background-color', '#f1f1f1')]},
                                                {'selector': 'td', 'props': [('padding', '8px'), ('border-bottom', '1px solid #ddd')]},
                                                {'selector': 'th:first-child, td:first-child', 'props': [('text-align', 'left')]}
                                            ])
                                        
                                        # Format the email body with better styling
                                        now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                                        yes_percent = (yes_votes / total_votes * 100) if total_votes > 0 else 0
                                        no_percent = (no_votes / total_votes * 100) if total_votes > 0 else 0
                                        
                                        email_body = f"""
                                        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
                                            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                                                WestProp Voting Activity Report
                                            </h2>
                                            <p style="color: #555; font-size: 14px; margin-bottom: 20px;">
                                                Generated on: {now}<br>
                                                Total Votes: {total_votes}<br>
                                                Yes: {yes_votes} ({yes_percent:.1f}%) | No: {no_votes} ({no_percent:.1f}%)
                                            </p>
                                        """.format(
                                            date=now,
                                            total_votes=total_votes,
                                            yes_votes=yes_votes,
                                            no_votes=no_votes,
                                            yes_percent=yes_percent,
                                            no_percent=no_percent
                                        )
                                        
                                        with tempfile.TemporaryDirectory() as temp_dir:
                                            # Save visualizations to files
                                            img_paths = []
                                            
                                            try:
                                                # Save overall distribution chart
                                                fig1, ax1 = plt.subplots(figsize=(8, 4))
                                                vote_counts = recent_votes['Vote'].value_counts()
                                                vote_counts.plot(kind='bar', color=['#4CAF50', '#F44336'], ax=ax1)
                                                ax1.set_title('Vote Distribution')
                                                ax1.set_xlabel('Vote')
                                                ax1.set_ylabel('Count')
                                                
                                                # Save the figure
                                                vote_chart_path = os.path.join(temp_dir, 'vote_distribution.png')
                                                plt.tight_layout()
                                                plt.savefig(vote_chart_path, dpi=100, bbox_inches='tight')
                                                plt.close()
                                                
                                                # Add chart to email
                                                email_body += """
                                                <div style='margin-bottom: 30px;'>
                                                    <h4>Vote Distribution</h4>
                                                    <img src='cid:votechart' style='max-width: 100%; border: 1px solid #ddd; border-radius: 4px;'/>
                                                </div>
                                                """
                                                
                                                # Create and save the overall distribution donut chart
                                                fig_donut, ax_donut = plt.subplots(figsize=(8, 8))
                                                wedges, texts, autotexts = ax_donut.pie(
                                                    vote_counts,
                                                    labels=vote_counts.index,
                                                    autopct='%1.1f%%',
                                                    colors=['#4CAF50', '#F44336'],
                                                    startangle=90,
                                                    wedgeprops=dict(width=0.4, edgecolor='white'),
                                                    textprops={'fontsize': 10, 'weight': 'bold'}
                                                )
                                                centre_circle = plt.Circle((0,0), 0.6, fc='white')
                                                ax_donut.add_artist(centre_circle)
                                                ax_donut.axis('equal')
                                                ax_donut.set_title('Overall Vote Distribution', fontsize=12, pad=20, fontweight='bold')
                                                
                                                # Add total votes in center
                                                ax_donut.text(0, 0, f"Total\n{total_votes} votes", 
                                                           ha='center', va='center', 
                                                           fontsize=12, fontweight='bold')
                                                
                                                donut_chart_path = os.path.join(temp_dir, 'donut_chart.png')
                                                plt.tight_layout()
                                                plt.savefig(donut_chart_path, dpi=100, bbox_inches='tight')
                                                plt.close()
                                                
                                                # Add donut chart to email
                                                email_body += """
                                                <div style='margin: 30px 0; text-align: center;'>
                                                    <h4>Overall Vote Distribution</h4>
                                                    <img src='cid:donutchart' style='max-width: 100%; max-height: 400px; border: 1px solid #ddd; border-radius: 8px;'/>
                                                </div>
                                                """
                                                
                                                # If we have location data, add a location-based chart
                                                if 'Project' in recent_votes.columns:
                                                    # Calculate location votes
                                                    location_votes = recent_votes.groupby('Project')['Vote'].value_counts().unstack(fill_value=0)
                                                    location_votes['Total'] = location_votes.get('Yes', 0) + location_votes.get('No', 0)
                                                    location_votes = location_votes.sort_values('Total', ascending=False)
                                                    
                                                    # Create location chart
                                                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                                                    location_votes[['Yes', 'No']].plot(kind='bar', stacked=True, 
                                                                                   color=['#4CAF50', '#F44336'], ax=ax2)
                                                    ax2.set_title('Votes by Project')
                                                    ax2.set_xlabel('Project')
                                                    ax2.set_ylabel('Number of Votes')
                                                    ax2.legend(title='Vote')
                                                    plt.xticks(rotation=45, ha='right')
                                                    
                                                    # Save the figure
                                                    location_chart_path = os.path.join(temp_dir, 'location_votes.png')
                                                    plt.tight_layout()
                                                    plt.savefig(location_chart_path, dpi=100, bbox_inches='tight')
                                                    plt.close()
                                                    
                                                    # Add location chart to email
                                                    if 'Project' in recent_votes.columns:
                                                        email_body += """
                                                        <div style='margin-top: 30px;'>
                                                            <h4>Votes by Project</h4>
                                                            <img src='cid:bylocation' style='max-width: 100%; border: 1px solid #ddd; border-radius: 4px;'/>
                                                        </div>
                                                        """
                                                
                                                # Add the data table
                                                email_body += """
                                                <div style='margin-top: 30px;'>
                                                    <h4>Recent Votes</h4>
                                                    {}
                                                </div>
                                                """.format(recent_votes.tail(10).to_html(index=False, classes='dataframe', border=0, 
                                                                                     table_id='voteTable'))
                                                
                                                # Close the HTML
                                                email_body += """
                                                    <p style='margin-top: 30px; color: #777; font-size: 12px;'>
                                                        This is an automated message. Please do not reply to this email.
                                                    </p>
                                                </div>
                                                """
                                                
                                                # Prepare attachments and image paths
                                                image_paths = [vote_chart_path, donut_chart_path]
                                                image_cids = ['votechart', 'donutchart']
                                                
                                                if 'Project' in recent_votes.columns and os.path.exists(location_chart_path):
                                                    image_paths.append(location_chart_path)
                                                    image_cids.append('bylocation')
                                                
                                                # Send the email with proper image attachments
                                                if send_email(
                                                    recipient=email,
                                                    subject=subject,
                                                    body=email_body,
                                                    is_html=True,
                                                    image_paths=image_paths,
                                                    image_cids=image_cids
                                                ):
                                                    status_container.success("✅ Report sent successfully!")
                                                else:
                                                    status_container.error("❌ Failed to send email. Please check the email configuration.")
                                                    logger.error(f"Failed to send email to {email}")
                                                
                                            except Exception as e:
                                                status_container.error("❌ Error generating visualizations. Sending text-only report...")
                                                if send_email(email, subject, email_body, is_html=True):
                                                    status_container.success("✅ Text-only report sent successfully!")
                                                else:
                                                    status_container.error("❌ Failed to send text-only email.")
                                    except Exception as e:
                                        status_container.error(f"❌ Error sending email: {str(e)}")
                                        st.error("Please check the logs for more details.")
                                        import traceback
                                        st.error(traceback.format_exc())
        
        except FileNotFoundError:
            st.warning("No votes recorded yet.")
        except Exception as e:
            st.error(f"Error loading vote data: {str(e)}")

    # Always show logout button when logged in
    if st.session_state.voting_admin_logged_in:
        if st.button("🔓 Logout", key="logout_btn"):
            # Clear all voting admin related session state
            st.session_state.voting_admin_logged_in = False
            # Clear any navigation flags
            if 'go_to_roi_map' in st.session_state:
                del st.session_state['go_to_roi_map']
            # Force a rerun to update the UI
            st.rerun()

    # === Optional Vote Summary Chart ===
    if st.session_state.get("admin_analytics_logged_in", False):
        st.subheader("📊 Vote Summary by Project")
    
    # ... rest of the code remains the same ...
        try:
            vote_df = pd.read_csv("vote_results.csv")
            if vote_df.empty:
                st.info("No votes yet. Chart will appear once votes are recorded.")
            else:
                # Count Yes/No votes per project
                vote_counts = vote_df.groupby(["Project", "Vote"]).size().unstack(fill_value=0)
                if "Yes" not in vote_counts.columns:
                    vote_counts["Yes"] = 0
                if "No" not in vote_counts.columns:
                    vote_counts["No"] = 0
                vote_counts = vote_counts[["Yes", "No"]]

                # Plot as grouped bar chart
                fig, ax = plt.subplots(figsize=(8, 5))
                vote_counts[["Yes", "No"]].plot(kind="bar", ax=ax, color=["#4CAF50", "#F44336"])
                ax.set_title("Would You Invest? — Votes per Project")
                ax.set_ylabel("Number of Votes")
                ax.set_xlabel("Project")
                plt.xticks(rotation=45, ha="right")
                st.pyplot(fig)

                # --- Add download button for the chart ---
                buf = io.BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                st.download_button(
                    label="📥 Download Vote Summary Chart (PNG)",
                    data=buf,
                    file_name="vote_summary_chart.png",
                    mime="image/png"
                )
        except FileNotFoundError:
            st.warning("No votes recorded yet. Cast some votes to populate this chart.")
        except pd.errors.EmptyDataError:
            st.info("Voting file is empty. No votes have been recorded yet.")
        except Exception as e:
            st.error(f"An error occurred while generating the chart: {e}")

elif page == "📍 Project Profiles":
    st.title("📍 WestProp Project Profiles")

    # Get project names that have profile info
    available_projects = list(project_profiles_info.keys())

    selected_project = st.selectbox("Select a Project to View Profile", options=available_projects)

    if selected_project:
        profile = project_profiles_info[selected_project]

        st.subheader(selected_project)

        # Display Image
        if profile.get("image") and os.path.exists(profile["image"]):
            st.image(profile["image"], use_container_width=True)
        else:
            # Check if the key exists but path is wrong, or if key is missing
            if profile.get("image"):
                 st.warning(f"Image file not found at path: {profile['image']}")
            else:
                 st.info(f"Image not available for {selected_project}.")

        # Display Description
        if profile.get("description"):
            st.markdown(profile["description"])
        else:
            st.info("Description not available.")

        # Display Link
        if profile.get("url"):
            # Basic check if URL seems valid (starts with http)
            if profile["url"].startswith("http"):
                 st.markdown(f"[➡️ Visit Official Project Page]({profile['url']})", unsafe_allow_html=True)
                 # Add specific note for potentially broken link
                 if "millenium-serviced-apartments" in profile["url"]:
                     st.caption("_Note: This specific link may be outdated based on recent checks._")
            else:
                 st.warning("Project URL seems invalid or missing.")
        else:
            st.info("Official project link not available.")

    st.markdown("---")

# ---  📊INVESTMENT MODELS PAGE ---
elif page == "📊 Investment Models":
    st.title("📊 Investment Models")
    st.markdown("Explore various investment models and strategies applicable to real estate.")

    st.subheader("1. Buy-to-Let Strategy")
    st.write("**Description:** Purchasing a property with the intention of renting it out to generate rental income and benefit from capital appreciation.")
    st.write("**Key Metrics:** Rental Yield, ROI, Vacancy Rate.")
    st.write("**Applicability:** Ideal for stable markets and investors seeking passive income.")

    st.subheader("2. Fix and Flip Strategy")
    st.write("**Description:** Buying undervalued properties, renovating them, and selling them for a profit in a short period.")
    st.write("**Key Metrics:** Renovation Costs, After Repair Value (ARV), Holding Costs.")
    st.write("**Applicability:** Requires strong market knowledge, renovation expertise, and access to capital.")

    st.subheader("3. Real Estate Investment Trusts (REITs)")
    st.write("**Description:** Companies that own, operate, or finance income-producing real estate. They are publicly traded like stocks.")
    st.write("**Key Metrics:** Dividend Yield, Funds From Operations (FFO).")
    st.write("**Applicability:** Offers liquidity and diversification without direct property ownership. Suitable for passive investors.")

    st.subheader("4. Property Development")
    st.write("**Description:** Acquiring land and constructing new buildings or redeveloping existing ones for sale or rent.")
    st.write("**Key Metrics:** Development Costs, Sales Revenue, Project Timeline.")
    st.write("**Applicability:** High capital requirement and risk, but potential for significant returns.")

    st.subheader("5. Short-Term Rentals (e.g., Airbnb)")
    st.write("**Description:** Renting out properties for short durations, often to tourists or business travelers.")
    st.write("**Key Metrics:** Occupancy Rate, Average Daily Rate (ADR), Management Fees.")
    st.write("**Applicability:** Can generate higher income than long-term rentals but requires more active management and is subject to tourism trends.")

    st.markdown("--- ")
    st.info("**Disclaimer:** This information is for educational purposes only and does not constitute financial advice. Always consult with a financial professional before making investment decisions.")

    st.title("📊 Compare Investment Models")

    model_choice = st.selectbox("Choose an Investment Type", ["Direct Purchase", "Radisson REIT (Seatrite 5)"])

    if model_choice == "Direct Purchase":
        st.subheader("🏠 Direct Property Purchase")

        st.markdown("""
        **🔹 Entry Point:** Varies by project ($70k – $1.6M)
        **🔹 Payment Terms:** 20–30% deposit, balance over 6–24 months
        **🔹 Return Type:** Rental income + Capital appreciation
        **🔹 Risks:** Market volatility, maintenance costs
        **🔹 Benefits:** Full ownership, resale flexibility, value growth
        """)

        st.markdown("### 📈 Simulate Returns (Direct Purchase)")

        purchase_price = st.number_input("Purchase Price (USD)", 50000, 2000000, 110000, step=1000, help="Total amount paid to acquire the property." )
        annual_rent = st.number_input("Expected Annual Rental Income (USD)", 1000, 100000, 12000, step=500, help="Estimated rental income per year.")
        appreciation = st.slider("Estimated Annual Appreciation (%)", 0, 20, 10, help="Expected % increase in property value per year." )
        years = st.slider("Investment Duration (Years)", 1, 30, 5, help="How long you plan to hold the investment." )

        total_rental = annual_rent * years
        # Corrected capital gain calculation
        capital_gain = purchase_price * ((1 + appreciation / 100) ** years) - purchase_price
        total_return = total_rental + capital_gain
        annualized_roi = ((total_return / purchase_price) ** (1/years) - 1) * 100 if years > 0 and purchase_price > 0 else 0

        st.metric("Total Estimated Return", f"${total_return:,.0f}")
        st.metric("Annualized ROI", f"{annualized_roi:.2f}%")

    elif model_choice == "Radisson REIT (Seatrite 5)":
        st.subheader("🏨 Radisson REIT (Seatrite 5 Trust)")
        st.markdown("""
        **🔹 Entry Point:** From $500
        **🔹 Payment Terms:** Upfront investment
        **🔹 Return Type:** Guaranteed 8% USD annual return (paid quarterly)
        **🔹 Risks:** Lower potential upside vs direct ownership, liquidity constraints
        **🔹 Benefits:** Hassle-free, professional management (Radisson), guaranteed return, capital protection (buy-back)
        """)
        st.markdown("### 📈 Simulate Returns (REIT)")
        investment_amount = st.number_input("Investment Amount (USD)", 500, 1000000, 10000, step=100, help="How much you’re investing in the REIT.")
        reit_years = st.slider("Investment Duration (Years)", 1, 10, 5, key="reit_years", help="Duration you plan to hold the REIT investment.")

        annual_return_reit = investment_amount * 0.08
        total_return_reit = annual_return_reit * reit_years

        st.metric("Annual Return (8% Guaranteed)", f"${annual_return_reit:,.2f}")
        st.metric(f"Total Return over {reit_years} Years", f"${total_return_reit:,.2f}")

elif page == "💸 Payment Plan Calculator":
    st.title("💸 Payment Plan Calculator")
    st.markdown("Estimate your monthly payments for a property.")

    st.subheader("Loan Details")
    property_price = st.number_input("Property Price (USD)", min_value=10000, value=150000, step=1000)
    down_payment_percentage = st.slider("Down Payment (%)", 0, 100, 20, step=1)
    interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.1, value=7.0, step=0.1, format="%.1f")
    loan_term_years = st.slider("Loan Term (Years)", 5, 30, 15, step=1)

    down_payment_amount = property_price * (down_payment_percentage / 100)
    loan_amount = property_price - down_payment_amount

    # Calculate monthly interest rate and number of payments
    monthly_interest_rate = interest_rate / 100 / 12

    number_of_payments = loan_term_years * 12

    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**number_of_payments) / ((1 + monthly_interest_rate)**number_of_payments - 1)
    else:
        monthly_payment = loan_amount / number_of_payments

    st.subheader("Payment Summary")
    st.write(f"**Property Price:** ${property_price:,.2f}")
    st.write(f"**Down Payment ({down_payment_percentage}%):** ${down_payment_amount:,.2f}")
    st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
    st.write(f"**Monthly Payment:** ${monthly_payment:,.2f}")
    st.write(f"**Total Payments:** ${monthly_payment * number_of_payments:,.2f}")
    st.write(f"**Total Interest Paid:** ${monthly_payment * number_of_payments - loan_amount:,.2f}")
    st.write("**Applicability:** Can generate higher income than long-term rentals but requires more active management and is subject to tourism trends.")

    st.markdown("--- ")
    st.info("**Disclaimer:** This calculator provides estimates only. Actual loan terms and payments may vary. Consult with a financial institution for precise figures.")

# --- PROPERTY BROWSER PAGE (NEW) ---
elif page == "🔍 Property Browser":
    st.title("🔍 Advanced Property Browser & Comparison")
    st.markdown("Filter WestProp properties based on your criteria and compare selections.")

    # --- Add Filter Widgets to Sidebar ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Properties")

    # Project Filter
    selected_projects = st.sidebar.multiselect("Select Project(s)", options=projects, default=projects)

    # Property Type Filter
    selected_types = st.sidebar.multiselect("Select Property Type(s)", options=property_types, default=property_types)

    # Price Range Filter
    min_price, max_price = int(properties_df["price"].min()), int(properties_df["price"].max())
    selected_price = st.sidebar.slider("Price Range (USD)", min_value=min_price, max_value=max_price, value=(min_price, max_price))

    # Amenities Filter
    selected_amenities = st.sidebar.multiselect("Required Amenities", options=amenities_options, help="Select the features you want in a property, like pool or gym.")

    # Status Filter
    selected_statuses = st.sidebar.multiselect("Select Status(es)", options=statuses, default=statuses)

    # Lazy load property listings
    items_per_page = 9
    page = st.session_state.get('property_page', 1)

    def show_properties(page, items_per_page):
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_properties))
        
        # Show current page of properties
        for i in range(0, end_idx - start_idx, 3):
            cols = st.columns(3)
            for j in range(3):
                idx = start_idx + i + j
                if idx < end_idx:
                    with cols[j]:
                        create_property_card(filtered_properties.iloc[idx].to_dict())
        
        return end_idx

    # Show pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if page > 1 and st.button("⬅️ Previous"):
            st.session_state.property_page = page - 1
            st.experimental_rerun()

    with col3:
        total_pages = (len(filtered_properties) + items_per_page - 1) // items_per_page
        if page < total_pages and st.button("Next ➡️"):
            st.session_state.property_page = page + 1
            st.experimental_rerun()

    # Show current page of properties
    show_properties(page, items_per_page)

    # --- Filtering Logic ---
    filtered_properties = properties_df.copy()

    # Apply filters
    if selected_projects:
        filtered_properties = filtered_properties[filtered_properties["project"].isin(selected_projects)]

    if selected_types:
        filtered_properties = filtered_properties[filtered_properties["property_type"].isin(selected_types)]

    filtered_properties = filtered_properties[
        (filtered_properties["price"] >= selected_price[0]) & (filtered_properties["price"] <= selected_price[1])
    ]

    if selected_amenities:
        # Check if all selected amenities are present in the property's amenity list
        def check_amenities(prop_amenities):
            if isinstance(prop_amenities, list):
                return all(amenity in prop_amenities for amenity in selected_amenities)

    if selected_statuses:
        filtered_properties = filtered_properties[filtered_properties["status"].isin(selected_statuses)]

    # --- Display Filtered Results & Comparison Selection ---
    st.subheader(f"🔎 Found {len(filtered_properties)} Properties Matching Filters")

    compare_list = []
    if not filtered_properties.empty:
        # Initialize the compare list in session state if it doesn't exist
        if 'compare_indices' not in st.session_state:
            st.session_state.compare_indices = []

        for index, row in filtered_properties.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{row['project']} - {row['property_type']}**")
                st.markdown(f"Price: ${row['price']:,} | Status: {row['status']}")
                # Show amenities concisely
                if isinstance(row['amenities'], list):
                    st.markdown(f"_Amenities:_ {', '.join(row['amenities'][:3])}{'...' if len(row['amenities']) > 3 else ''}")
                if row['url'] and isinstance(row['url'], str) and row['url'].startswith('http'):
                    st.markdown(f"[More Details]({row['url']})", unsafe_allow_html=True)
                else:
                    st.caption("More Details: Link unavailable")
            with col2:
                # Use a unique key for each checkbox based on the DataFrame index
                # Check if index is already in the comparison list (persists across reruns)
                is_checked = index in st.session_state.compare_indices
                if st.checkbox("Compare", value=is_checked, key=f"compare_{index}"):
                    if index not in st.session_state.compare_indices:
                         st.session_state.compare_indices.append(index) # Add index if checked and not already there
                else:
                    if index in st.session_state.compare_indices:
                        st.session_state.compare_indices.remove(index) # Remove index if unchecked

            st.markdown("---")
        # Use the session state list for comparison
        compare_list = st.session_state.compare_indices
    else:
        st.warning("No properties match the selected filters.")
        # Clear comparison list if filters result in empty set
        if 'compare_indices' in st.session_state:
            st.session_state.compare_indices = []

    # --- Comparison Section ---
    st.subheader("⚖️ Property Comparison")

    if len(compare_list) >= 2:
        properties_to_compare = properties_df.loc[compare_list]
        num_columns = len(properties_to_compare)
        cols = st.columns(num_columns)

        # Define attributes to compare
        attributes_to_show = ["project", "property_type", "price", "size_sqm", "bedrooms", "status", "amenities", "payment_terms"]

        for i, index in enumerate(properties_to_compare.index):
            with cols[i]:
                st.markdown(f"#### {properties_to_compare.loc[index, 'project']}")
                st.markdown(f"##### {properties_to_compare.loc[index, 'property_type']}")
                for attr in attributes_to_show:
                    value = properties_to_compare.loc[index, attr]

                    # Handle list type first (amenities)
                    if attr == "amenities" and isinstance(value, list):
                        if value: # Check if the list is not empty
                            st.markdown(f"**{attr.replace('_', ' ').title()}:**")
                            for amenity in value:
                                st.markdown(f"- {amenity}")
                        # else: optionally handle empty list case if needed

                    # Handle other types (non-lists)
                    elif not isinstance(value, list) and pd.notna(value):
                        if attr == "price":
                            st.markdown(f"**{attr.replace('_', ' ').title()}:** ${value:,}")
                        elif attr == "size_sqm":
                             st.markdown(f"**{attr.replace('_', ' ').title()}:** {value:.1f}") # Format float
                        elif attr == "bedrooms":
                             st.markdown(f"**{attr.replace('_', ' ').title()}:** {int(value)}") # Format as int
                        else:
                            st.markdown(f"**{attr.replace('_', ' ').title()}:** {value}")
                    # Optionally handle NaN/None cases for non-list types if needed
                    elif pd.isna(value) and not isinstance(value, list):
                         st.markdown(f"**{attr.replace('_', ' ').title()}:** Not Available")
    
    # --- Image Optimization ---
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_image(image_path, width=300):
        """Load and resize image with caching"""
        try:
            img = Image.open(image_path)
            # Resize image to optimize loading
            img.thumbnail((width, width))
            return img
        except Exception as e:
            return None

    def create_property_card(property_data, show_contact=False):
        """Create a property card with optimized image loading"""
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Use placeholder while loading
                with st.spinner(''):
                    img_placeholder = st.empty()
                    img = None
                    
                    # Load image in background
                    if property_data.get('images') and len(property_data['images']) > 0:
                        img = load_image(property_data['images'][0])
                    
                    # Display image or placeholder
                    if img:
                        img_placeholder.image(
                            img,
                            use_column_width=True,
                            caption=property_data['name']
                        )
                    else:
                        img_placeholder.image(
                            "westprop_logo.png",
                            use_column_width=True,
                            caption="Image not available",
                            width=150
                        )
            
            with col2:
                st.subheader(property_data['name'])
                st.caption(f"Type: {property_data['type']}")
                st.write(f"**Price:** {property_data['price']}")
                st.write(f"**ROI:** {property_data['roi']}")
                st.write(f"**Status:** {property_data['status']}")
    def get_profile_recommendations(profile_type, properties_data):
        """Get property recommendations based on investor profile type"""
        profile_mapping = {
            "Diaspora Investor": {
                "filters": lambda x: x['name'] in ['Radisson Aparthotel', 'Pomona City Flats', 'Millennium Heights'],
                "sort_key": lambda x: -float(x.get('roi', '0%').replace('%', '').split('-')[0]) if x.get('roi', '0%') != 'N/A' else 0
            },
            "Local First-Time Buyer": {
                "filters": lambda x: x['name'] in ['Pomona City Flats', 'Pokugara Townhouses', 'Millennium Heights'] and \
                                   (x['name'] != 'Millennium Heights' or (float(x.get('price', '$0').replace('$', '').replace('From ', '').replace(',', '').split(' ')[0]) >= 50000 and \
                                                                          float(x.get('price', '$0').replace('$', '').replace('From ', '').replace(',', '').split(' ')[0]) <= 130000)) and \
                                   (any(size in x.get('type', '') for size in ['Studio', '1 Bed', '2 Bed', '3 Bed']) or \
                                    (x['name'] == 'Millennium Heights' and x.get('specs', {}).get('Bedrooms', '') in ['1-3', '1 Bed', '2 Bed'])),
                "sort_key": lambda x: float(x.get('price', '$0').replace('$', '').replace('From ', '').replace(',', '').split(' ')[0])
            },
            "Family Upsizing": {
                "filters": lambda x: x['name'] in ['Pokugara Townhouses', 'The Hills Lifestyle Estate'],
                "sort_key": lambda x: -float(x.get('price', '$0').replace('$', '').replace('From ', '').replace(',', '').split(' ')[0])
            },
            "Retiree": {
                "filters": lambda x: x['name'] in ['The Hills Lifestyle Estate'] or any(keyword in x.get('description', '').lower() for keyword in ['peaceful', 'secure', 'low maintenance', 'retirement', 'lifestyle']),
                "sort_key": lambda x: float(x.get('price', '$0').replace('$', '').replace('From ', '').replace(',', '').split(' ')[0])
            },
            "Passive Income Seeker": {
                "filters": lambda x: x['name'] in ['Radisson Aparthotel', 'Millennium Heights'] or any(keyword in x.get('description', '').lower() for keyword in ['rental', 'income', 'yield', 'investment', 'aparthotel', 'serviced']),
                "sort_key": lambda x: -float(x.get('roi', '0%').replace('%', '').split('-')[0]) if x.get('roi', '0%') != 'N/A' else 0
            }
        }
        
        filters = profile_mapping.get(profile_type, {})
        if not filters:
            return []
            
        matched = [p for p in properties_data if filters['filters'](p)]
        
        try:
            matched.sort(key=filters['sort_key'])
        except (ValueError, AttributeError, IndexError):
            # If sorting fails, return as is
            pass
            
        return matched[:5]  # Return top 5 matches

def show_property_details(property_data):
    """Show detailed view of a selected property"""
    # Back button at the top
    if st.button("← Back to Properties", key="back_to_properties_btn"):
        if 'selected_property' in st.session_state:
            del st.session_state.selected_property
        if 'show_booking_form' in st.session_state:
            del st.session_state.show_booking_form
        st.rerun()
        
    st.title(property_data.get('name', 'Property Details'))
    
    # Image gallery
    if property_data.get('images'):
        st.image(property_data['images'][0], use_container_width=True)
    
    # Main details
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Price", property_data.get('price', 'N/A'))
        st.metric("ROI", property_data.get('roi', 'N/A'))
        st.metric("Status", property_data.get('status', 'N/A'))
    with col2:
        st.metric("Location", property_data.get('location', 'N/A'))
        st.metric("Type", property_data.get('type', 'N/A'))
        st.metric("Completion", property_data.get('completion', 'N/A'))
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📝 Description", "🏗️ Specifications", "💡 Features"])
    
    with tab1:
        st.write(property_data.get('description', 'No description available'))
    
    with tab2:
        if 'specs' in property_data:
            for key, value in property_data['specs'].items():
                st.markdown(f"**{key}:** {value}")
    
    with tab3:
        if 'highlights' in property_data:
            st.subheader("Highlights")
            for item in property_data['highlights']:
                st.markdown(f"- {item}")
                
        if 'amenities' in property_data:
            st.subheader("Amenities")
            cols = st.columns(3)
            for i, amenity in enumerate(property_data['amenities']):
                cols[i%3].markdown(f"✓ {amenity}")
    
    # Contact and action buttons
    st.divider()
    st.subheader("Interested?")
    st.markdown(f"📞 {property_data.get('contact', 'Contact sales for more information')}")
    
    if st.button("Schedule a Viewing", type="primary"):
        st.session_state.show_booking_form = True
    
    if st.session_state.get('show_booking_form', False):
        with st.form("viewing_form"):
            st.write("### Schedule a Viewing")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            date = st.date_input("Preferred Date")
            submitted = st.form_submit_button("Request Viewing")
            if submitted and name and email and phone and date:
                # Create viewing request data
                import csv
                from datetime import datetime
                import os
                
                request_data = {
                    'timestamp': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'property_name': property_data.get('name', 'N/A'),
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'preferred_date': date.strftime('%Y-%m-%d'),
                    'status': 'New'
                }
                
                # Define CSV file path
                csv_file = 'viewing_requests.csv'
                file_exists = os.path.isfile(csv_file)
                
                # Write to CSV
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=request_data.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(request_data)
                
                st.success("Viewing request submitted! Our team will contact you shortly.")
                st.session_state.show_booking_form = False
            elif submitted:
                st.error("Please fill in all required fields.")

        if st.button("← Back to Matches"):
            if 'selected_property' in st.session_state:
                del st.session_state.selected_property
            if 'show_booking_form' in st.session_state:
                del st.session_state.show_booking_form
            st.rerun()

# Show detailed property view if selected
if 'selected_property' in st.session_state:
    show_property_details(st.session_state.selected_property)

elif page == "🧬 Investor Match":
    st.title("🧬 Smart Property Match")
    st.markdown("Find properties that match your investment goals and lifestyle needs")
    
    # Profile Selection
    profile = st.selectbox("Select Your Investor Profile", [
        "Diaspora Investor",
        "Local First-Time Buyer",
        "Family Upsizing",
        "Retiree",
        "Passive Income Seeker"
    ])
    
    # Get matches
    matched_properties = get_matching_properties(profile, list(property_details.values()))
    
    # Display profile-specific insights
    st.subheader(f"🏆 Best Matches for {profile}")
    if not matched_properties:
        st.warning("No properties match your current criteria. Try adjusting your profile.")
    else:
        st.info(f"✨ Found {len(matched_properties)} properties matching your profile")
    
    # Display profile summary
    profile_summary = {
        "Diaspora Investor": {
            "description": "Low-maintenance units, REIT access, strong rental income",
            "budget": "$5,000 – $150,000",
            "focus": "Income over appreciation"
        },
        "Local First-Time Buyer": {
            "description": "Affordable units with installment options",
            "budget": "$50,000 – $130,000",
            "focus": "Long-term ownership and equity building"
        },
        "Family Upsizing": {
            "description": "Spacious units, secure gated estates, schools nearby",
            "budget": "$300,000 – $600,000",
            "focus": "Lifestyle + capital preservation"
        },
        "Retiree": {
            "description": "Peaceful environments, easy access, low stairs, security",
            "budget": "$100,000 – $350,000",
            "focus": "Lifestyle, not yield"
        },
        "Passive Income Seeker": {
            "description": "High rental demand, serviced models, professional management",
            "budget": "$5,000 – $300,000",
            "focus": "Yield, dividends, low effort"
        }
    }
    
    with st.expander("📊 Profile Summary", expanded=True):
        summary = profile_summary.get(profile, {})
        st.markdown(f"""
        **Investment Strategy:** {summary.get('description', 'N/A')}  
        **Suggested Budget:** {summary.get('budget', 'N/A')}  
        **ROI Focus:** {summary.get('focus', 'N/A')}
        """)
    
    # Display property cards
    st.subheader("🏠 Recommended Properties")
    for prop in matched_properties:
        st.markdown("---")  # Divider between cards
        create_property_card(prop, show_contact=True)

elif page == "🔧 Shell Unit Customizer":
    st.title("🔧 Shell Unit Customizer")
    st.markdown("Design your ideal shell unit and see potential costs.")

    st.subheader("Unit Specifications")
    num_bedrooms = st.slider("Number of Bedrooms", 1, 5, 3)
    num_bathrooms = st.slider("Number of Bathrooms", 1, 4, 2)
    unit_size_sqm = st.number_input("Unit Size (sqm)", min_value=50, value=150, step=10)

    st.subheader("Finishing Options")
    kitchen_finish = st.selectbox("Kitchen Finish", ["Basic", "Standard", "Premium"])
    bathroom_finish = st.selectbox("Bathroom Finish", ["Basic", "Standard", "Premium"])
    flooring_type = st.selectbox("Flooring Type", ["Tiles", "Laminate", "Hardwood"])

    st.subheader("Smart Feature Add-ons")
    add_solar = st.checkbox("Add Solar Panels")
    add_water_recycling = st.checkbox("Add Water Recycling System")
    add_smart_locks = st.checkbox("Add Smart Locks")
    add_smart_thermostats = st.checkbox("Add Smart Thermostats")
    add_integrated_security = st.checkbox("Add Integrated Security System")
    add_ev_charging = st.checkbox("Add EV Charging Station")

    # --- Cost Estimation Logic (Simplified Example) ---
    base_cost_per_sqm = 800  # USD per sqm for basic shell
    total_cost = unit_size_sqm * base_cost_per_sqm

    # Adjust for bedrooms/bathrooms (simplified)
    total_cost += (num_bedrooms - 1) * 5000  # Each additional bedroom adds cost
    total_cost += (num_bathrooms - 1) * 3000  # Each additional bathroom adds cost

    # Finishing costs
    if kitchen_finish == "Standard":
        total_cost += 7000
    elif kitchen_finish == "Premium":
        total_cost += 15000

    if bathroom_finish == "Standard":
        total_cost += 5000
    elif bathroom_finish == "Premium":
        total_cost += 10000

    if flooring_type == "Laminate":
        total_cost += unit_size_sqm * 10
    elif flooring_type == "Hardwood":
        total_cost += unit_size_sqm * 20

    # Smart feature costs (example figures)
    if add_solar:
        total_cost += 8000
    if add_water_recycling:
        total_cost += 3000
    if add_smart_locks:
        total_cost += 500
    if add_smart_thermostats:
        total_cost += 700
    if add_integrated_security:
        total_cost += 2500
    if add_ev_charging:
        total_cost += 4000

    st.subheader("Estimated Cost")
    st.metric("Total Estimated Cost", f"${total_cost:,.2f}")

    st.markdown("--- ")
    st.info("**Disclaimer:** This is a simplified cost estimator. Actual costs will vary based on specific materials, labor, and market conditions. Consult with a WestProp sales representative for a detailed quote.")

elif page == "♻️ Smart Feature Value Proposition":
    st.title("♻️ Smart Feature Value Proposition")
    st.markdown("Understand the financial and environmental benefits of smart features.")

    st.subheader("Estimated Monthly Savings per Feature")
    st.dataframe(smart_value_df)
    
    st.caption("🔎 Figures are based on Zimbabwe’s energy/water context, property market trends, and smart home ROI studies.")

    st.markdown("--- ")
    st.subheader("Beyond Savings: Additional Benefits")
    st.write("**☀️ Solar Panels:** Reduced electricity bills, lower carbon footprint, increased energy independence, potential for feed-in tariffs.")
    st.write("**💧 Water Recycling:** Significant reduction in water consumption, lower water bills, sustainable landscaping, reduced strain on municipal water supply.")
    st.write("**🔐 Smart Locks:** Enhanced security, remote access control, keyless entry convenience, improved property management for rentals.")
    st.write("**🌡️ Smart Thermostats:** Optimized energy usage for heating/cooling, remote temperature control, personalized comfort, reduced utility costs.")
    st.write("**🚨 Integrated Security:** Comprehensive home protection, remote monitoring, rapid response, peace of mind.")
    st.write("**🔌 EV Charging:** Convenience for electric vehicle owners, increased property appeal, future-proofing, potential for higher resale value.")

    st.markdown("--- ")
    st.info("**Note:** Savings are estimates and can vary based on usage, property size, and local utility rates. Environmental benefits contribute to a sustainable lifestyle and increased property value.")
elif page == "❓ Help":
    st.title("❓ Help & User Guide")
    st.markdown("""
Welcome to the **Smart Real Estate ROI Simulator**.

This dashboard helps you simulate and predict the **Return on Investment (ROI)** for WestProp properties, including:

- **Millennium Heights**
- **Pomona City**
- **The Hills Lifestyle Estate**
- **Pokugara Residential Estate**

---

## 🧭 How to Use

1. **Go to the Simulator tab**
2. Enter your property's market price and expected rent.
3. Toggle smart features (solar, recycling, smart locks).
4. See dynamic ROI results, savings, financial breakdowns, and predictions.
5. **Load Past Simulations** - Access previously saved simulations from the sidebar to review or modify them.

---

## 📈 ROI Metrics Explained

- **Traditional ROI (Net):** Calculated based on annual rental income minus estimated annual expenses (property tax, maintenance, insurance, agent fees), divided by the market price.
- **Smart ROI (Net):** Similar to Traditional ROI, but includes the estimated annual savings from smart features, increasing the net income.
- **Predicted ROI (Model):** An ROI forecast generated by our machine learning model, considering various property attributes and smart features.

## 🏙️ About Location & Property Type

In the Simulator, you'll notice fields for Location Suburb and Property Type. Here's what you should know:

- These fields are collected for future enhancements and data collection
- Currently, they have minimal impact on the ROI calculations
- The model primarily focuses on property characteristics (size, features) and smart technology
- We're working to enhance location-based predictions in future updates

For the most accurate results, focus on adjusting the property specifications and smart features that directly impact energy savings and operational efficiency.

---

## 🗂️ My Simulations

- Instantly review and reload your past simulation sessions.

---

## 🗺️ ROI Map Tips

- Use the **ROI Map** to explore project locations and ROI heat levels.
- Click any location to simulate potential ROI at that point.
- After clicking, you can cast a **"Would You Invest?" vote** to help us understand investor sentiment.

---

## 📍 Project Profiles

Explore detailed profiles of WestProp developments:

- The Hills Lifestyle Estate
- Millennium Heights
- Pomona City
- Pokugara Townhouses
- Radisson Apartments

Includes images, amenities, status, and direct links to official pages.

---

## 📊 Investment Models

- Compare **Direct Purchase** vs **Radisson REIT**.
- Simulate returns, risk, and income.
- Designed for both retail investors and institutional buyers.

---

## 💸 Payment Plan Calculator

- Pokugara and Hills-specific calculators.
- See deposit, commitment fees, monthly payment timelines.
- Includes interest simulation for Hills' 24-month plan.

---

## 🔍 Property Browser

- Advanced filters by project, type, price, status, amenities.
- Compare properties side-by-side.
- Based on real WestProp listing data.

---

## 🧬 Investor Match

- Pick your profile (Diaspora Investor, Retiree, First-Time Buyer, etc.).
- Get auto-matched to best-fit projects + rationale.
- Uses curated logic from WestProp's research & buyer personas.

---

## 🔧 Shell Unit Customizer

- Specifically for Millennium Heights Block 4
- Estimate total cost to finish shell units using:
  - Standard
  - Premium
  - Custom finishing

---

## ♻️ Smart Feature Value Proposition

- Highlights ROI uplift, resale value, and sustainability impact of smart features:
  - Solar Power
  - Water Recycling
  - Smart Locks
- Backed by Zimbabwean market data

---

## 🛡️ Admin Analytics Dashboard (Staff Only)

WestProp staff can access a dedicated Admin Analytics Dashboard for deeper insights:

- View simulation activity trends
- See the most popular simulated market prices
- Explore investor sentiment heatmaps
- Download raw simulation and voting data

**To access:**  
Log in as admin via the Admin Analytics tab.

> _Note: These features are restricted to authorized staff for data privacy and business security._

---

### ℹ️ About Tab

- Learn about the dashboard's purpose and structure
- Read about WestProp's mission, CEO Ken Sharpe, and values.
- Get context for how each tool supports investor insights and smart growth.

---

## 📉 Market Trends & Analytics

- Explore national and regional price trends, rental yields, and smart feature adoption.

## 🔔 Alerts Tab

- Subscribe for email updates on new projects, price changes, and investment opportunities.

## 🏆 Community Insights

- See the most simulated projects, top ROI locations, and investor sentiment trends.

## 🌀 ROI Sensitivity Analysis (Simulator Tab)

- Run what-if scenarios to see how changes in rent, price, or smart feature adoption affect ROI.
- Use the **Tornado Chart Mode** toggle to switch between:
  - **Tornado Chart Mode:** Shows the impact of individual features on ROI
  - **Full Impact (0%→100%)**: See the maximum possible ROI impact for each variable.
  - **What-If (Current→100%)**: See the ROI impact of increasing each variable from its current value to 100%.
  - **Feature Comparison Mode:** Compares the ROI impact of all smart features side by side
- The tornado chart and table below it will update to show which factors have the biggest effect on your returns.

## 💡 Tooltips

Hover over any sidebar element, slider, or checkbox to get quick explanations.

---

## Data & Assumptions

The simulator uses a dataset of real estate properties in Harare, Zimbabwe. All ROI calculations are estimates and are based on the provided input parameters and predefined expense rates.

Smart feature savings are based on general market research and may vary based on actual usage and local conditions.

## 📬 Need Support?

For questions, feedback, or collaboration inquiries, please email [tutu@westprop.com](mailto:tutu@westprop.com)

---
""")

    st.info("This platform was built to align with WestProp's tech-forward real estate vision. Thank you for exploring it!")

# --- ABOUT PAGE ---
elif page == "ℹ️ About":
    st.title("ℹ️ About This Dashboard")
    st.markdown("""
    **Welcome to the Smart Real Estate ROI Simulator by WestProp.**  
    This dashboard helps evaluate return on investment (ROI) on smart-enabled properties and promotes data-driven property development.

    ---

    ## 🚀 What’s New

   - 📉 **Market Trends & Analytics:** Explore national and regional price trends, rental yields, and smart feature adoption.
   - 🔔 **Alerts Tab:** Subscribe for email updates on new projects, price changes, and investment opportunities.
   - 🏆 **Community Insights:** See most simulated projects, top ROI locations, and investor sentiment trends.
   - 🌀 **ROI Sensitivity Analysis:** Run what-if scenarios in the Simulator tab to see how changes in rent, price, or features affect ROI.
   - 🗂️ **My Simulations:** Instantly review and reload your past simulation sessions.
   - 🛡️ **Admin Analytics Dashboard:** Secure, staff-only analytics for simulation trends, sentiment heatmaps, and raw data downloads.
                        
    ---
                
    ### Key Features:
    - 💰 ROI comparison: Traditional vs Smart
    - 🤖 AI-powered ROI predictions
    - 🗺️ Interactive ROI Map across WestProp projects
    - 🗳️ \'Would You Invest?\' voting system
    - 📄 Executive Summary downloads (PDF/CSV)
    - 📈 View project-specific ROI analytics for strategic insights  
    - ♻️ Smart Feature Value insights
    - 🧬 Investor-Profile matching
    - 💸 Payment plan calculators for Pokugara & The Hills
    ### Powered by:
    - **Streamlit**, **scikit-learn**, **Python**, **folium**, **Reportlab**, and **WestProp project data**
    
    👨‍💻 Built by Adonis Chiruka
                
     ## 🏢 About WestProp Holdings
                
    **Who We Are:**
     WestProp Holdings Limited is a multi-award-winning luxury properties developer and has been leading the property development industry in Harare, Zimbabwe, since 2007. We made history by becoming the first property development company to list on the Victoria Falls Stock Exchange on the 29th of April 2023.

    We have over sixteen years of experience in real estate development in Zimbabwe with a portfolio of completed and under-construction projects. Our strategic plan to develop real estate worth over US$5 billion is now in full swing with more than 1,000 residential units namely, Homeland 263, Pokugara Clusters Phase 1 and 2, Pokugara Residential homes/stands, Gunhill Rise, Pomona City stands phase 1A and phase 1B and C, Millennium Heights Apartments Block 1, 2,3 and 4. Our retail development, Mbudzi
    We are developing the land bank to establish a lasting legacy of valuable real estate in Zimbabwe. We aim to become the leading real estate developer for tomorrow’s market in Zimbabwe and Africa as a whole.

    In future, we plan to develop the Mall of Zimbabwe, which promises to be one of Africa’s largest shopping centres, a hub where people can eat, shop, work, and play. We also plan to elevate the tourism and hospitality sector with the development of a first-ever PGA Championship standard golf course, along with luxurious residential and hotel properties, as part of the US$280 million Golf Estate project          
                
    **Our Vision:**  
    Our Vision is to become the leading customer-centric developer of exceptional properties in Zimbabwe.

    **Our Mission:**  
    Our Mission is to delight our customers with the latest sustainable innovations incorporating modern designs in our residential and commercial offerings in Zimbabwe.

   

    **Core Values:**

    - 🛡️ **Integrity**  
      Be a trusted and reputable real estate company that meets all stakeholder requirements whilst offering significant returns by maximising investment opportunities in our premium projects.

    - 🌍 **Innovation / Sustainability**  
      Redefine market trends by focusing on customer needs, improving their quality of life while upholding our environmental responsibility.

    - 📣 **Accountability**  
      Empower our team to deliver best-in-class service and investment opportunities through a culture of mutual respect, transparency, and responsibility.

    - 🏆 **Excellence**  
      Lead the premium real estate industry with top-tier value propositions and unmatched product quality.

    **Notable Achievements:**
    - 🏆 Best High-Rise Development – African Property Awards  
    - 🌱 Environmental & Sustainability Award – National Property Expo  
    - 🥇 VFEX-listed pioneering lifestyle developer  
    - 🏘️ Flagship Projects: Millennium Heights, Pokugara, Pomona City, The Hills Lifestyle Estate, Radisson Serviced Apartments
""")
    
    st.image("ken_sharpe.jpg", width=300, caption="Ken Sharpe – CEO of WestProp Holdings")        
    st.markdown("""
    ## 👨🏽‍💼 About the CEO – Ken Sharpe

    Ken Sharpe is the visionary Executive Chairman and CEO of WestProp Holdings. Known for bold innovation and forward-thinking urban design, his mission is to:
    
    > “Build communities, not just properties.”  
    > “Make Zimbabwe a shining example of lifestyle real estate development in Africa.”
    
    Ken Sharpe founded WestProp in 2007 and has steered the company over the last fifteen years into a master planner, financier and largest property developer in Zimbabwe. He has a vision for the development of premium lifestyle communities in Harare and is a pioneer in the establishment of a public private partnership with the City of Harare to create commercial, industrial and residential estates.
    Through his stewardship, Ken has brought to life Pomona City, a 270-hectare mixed-use lifestyle estate that will offer its residents a trusted customer-centric ecosystem to live, work, play & shop. Most prestigious amongst his numerous awards is the Forbes Best of Africa Most Innovative CEO of the Year which Ken was awarded in 2021. He has also been awarded the ZNCC Businessman of the Year Award and numerous others. He has led landmark projects like Millennium Heights, The Hills Lifestyle Estate, Pokugara Residential Estate, Radisson Serviced Apartments, and Pomona City, while championing digital transformation and smart infrastructure in housing.

    📌 Featured in:
    - ZimReal Summit
    - Global Africa Business Initiative
    - Property Magazine Africa
""")

# --- ALERTS PAGE ---
elif page == "🔔 Alerts":
    st.title("🔔 Alerts & Notifications")
    st.markdown("Stay updated with important market changes, new listings, and personalized alerts.")
    
    # Subscription form for all users
    st.subheader("📩 Subscribe to Alerts")
    with st.form("email_subscription"):
        email = st.text_input("Your Email")
        frequency = st.selectbox("Alert Frequency", ["Daily", "Weekly", "Monthly"], index=1)
        interests = st.multiselect("Areas of Interest", 
                                ["New Listings", "Price Drops", "Market Trends", "Project Updates", "Investment Opportunities"])
        
        if st.form_submit_button("Subscribe"):
            if email and "@" in email:
                try:
                    # Ensure data directory exists
                    os.makedirs('data', exist_ok=True)
                    subscribers_file = 'data/email_alert_subscribers.csv'
                    
                    # Create or update the subscribers file
                    if not os.path.exists(subscribers_file):
                        with open(subscribers_file, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(['email', 'frequency', 'interests', 'subscribed_at', 'last_sent', 'status'])
                    
                    # Read existing data
                    df = pd.read_csv(subscribers_file) if os.path.exists(subscribers_file) else pd.DataFrame()
                    
                    # Ensure the DataFrame has the required columns
                    required_columns = ['email', 'frequency', 'interests', 'subscribed_at', 'last_sent', 'status']
                    for col in required_columns:
                        if col not in df.columns:
                            df[col] = ''
                    
                    # Update or add subscriber
                    if not df.empty and 'email' in df.columns and email in df['email'].values:
                        df.loc[df['email'] == email, 'frequency'] = frequency
                        df.loc[df['email'] == email, 'interests'] = ', '.join(interests)
                        df.loc[df['email'] == email, 'status'] = 'Active'
                        st.success("Your subscription preferences have been updated!")
                    else:
                        new_row = {
                            'email': email,
                            'frequency': frequency,
                            'interests': ', '.join(interests) if interests else '',
                            'subscribed_at': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'last_sent': '',
                            'status': 'Active'
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        st.success("Thank you for subscribing to our alerts!")
                    
                    # Save back to file
                    df.to_csv(subscribers_file, index=False)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.error("Please enter a valid email address.")
    
    # Admin section (only visible to admins)
    if st.session_state.get("is_admin", False):
        st.markdown("---")
        st.subheader("🔒 Admin: Manage Subscribers")
        st.success("🛡️ ADMIN MODE ACTIVE - You have full access to subscriber management")
        st.info("You can view and manage all subscribers below.")
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Define subscribers file path
        subscribers_path = os.path.join('data', 'email_alert_subscribers.csv')
        
        # Create empty subscribers file if it doesn't exist
        if not os.path.exists(subscribers_path):
            pd.DataFrame(columns=['email', 'name', 'frequency', 'interests', 'subscribed_at', 'last_sent', 'status']).to_csv(subscribers_path, index=False)
            st.warning("Created a new subscribers file as none existed.")
        
        # Load and display subscribers data
        st.write("### Current Subscribers")
        
        # Define required columns
        required_columns = ['email', 'name', 'frequency', 'interests', 'subscribed_at', 'last_sent', 'status']
        
        try:
            # Try to load existing subscribers
            subscribers_df = pd.read_csv(subscribers_path)
        
            # Ensure required columns exist
            for col in required_columns:
                if col not in subscribers_df.columns:
                    subscribers_df[col] = ''
            
            # Ensure name column exists and fill any missing values
            if 'name' not in subscribers_df.columns:
                subscribers_df['name'] = ''
            subscribers_df['name'] = subscribers_df['name'].fillna('')
            
            # Set default status for new entries
            if 'status' not in subscribers_df.columns:
                subscribers_df['status'] = 'Active'
            subscribers_df['status'] = subscribers_df['status'].fillna('Active')
        
        except FileNotFoundError:
            # If file doesn't exist, create an empty DataFrame with required columns
            subscribers_df = pd.DataFrame(columns=required_columns)
            subscribers_df['status'] = 'Active'  # Set default status for new entries
        except Exception as e:
            st.error(f"Error loading subscribers: {str(e)}")
            subscribers_df = pd.DataFrame(columns=required_columns)
            subscribers_df['status'] = 'Active'  # Set default status for new entries
        
        # Initialize editing state if not exists
        if 'editing_subscriber' not in st.session_state:
            st.session_state.editing_subscriber = None
            
        # Display subscribers with edit buttons
        for idx, subscriber in subscribers_df.iterrows():
            with st.expander(f"📧 {subscriber['email']}", expanded=False):
                # Show edit form when edit button is clicked
                if st.button(f"✏️ Edit {subscriber['email']}", key=f"edit_{idx}"):
                    st.session_state['editing_subscriber'] = idx
                
                if st.session_state.get('editing_subscriber') == idx:
                    # Show edit form
                    with st.form(key=f"edit_subscriber_{idx}"):
                        edited_email = st.text_input("Email", value=subscriber.get('email', ''))
                        edited_name = st.text_input("Name", value=subscriber.get('name', ''))
                        edited_frequency = st.selectbox(
                            "Frequency",
                            ["Daily", "Weekly", "Monthly"],
                            index=["Daily", "Weekly", "Monthly"].index(subscriber.get('frequency', 'Weekly'))
                        )
                        current_interests = [i.strip() for i in str(subscriber.get('interests', '')).split(',') if i.strip()]
                        edited_interests = st.multiselect(
                            "Interests",
                            ["New Listings", "Price Drops", "Market Trends", "Project Updates"],
                            default=[i for i in current_interests if i in ["New Listings", "Price Drops", "Market Trends", "Project Updates"]]
                        )
                        edited_status = st.selectbox(
                            "Status",
                            ["Active", "Inactive", "Unsubscribed"],
                            index=["Active", "Inactive", "Unsubscribed"].index(subscriber.get('status', 'Active'))
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                # Update the subscriber data
                                subscribers_df.at[idx, 'email'] = edited_email
                                subscribers_df.at[idx, 'name'] = edited_name
                                subscribers_df.at[idx, 'frequency'] = edited_frequency
                                subscribers_df.at[idx, 'interests'] = ", ".join(edited_interests)
                                subscribers_df.at[idx, 'status'] = edited_status
                                # Save changes
                                os.makedirs('data', exist_ok=True)
                                subscribers_df.to_csv("data/email_alert_subscribers.csv", index=False)
                                st.success("✅ Subscriber updated successfully!")
                                st.session_state.editing_subscriber = None
                                st.rerun()
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state.editing_subscriber = None
                                st.rerun()
                
                # Display subscriber details
                st.write(f"**Name:** {subscriber.get('name', 'N/A')}")
                st.write(f"**Frequency:** {subscriber.get('frequency', 'N/A')}")
                st.write(f"**Interests:** {subscriber.get('interests', 'N/A')}")
                st.write(f"**Status:** {subscriber.get('status', 'N/A')}")
                st.write(f"**Subscribed On:** {subscriber.get('subscribed_at', 'N/A')}")
                if subscriber.get('last_sent'):
                    st.write(f"**Last Email Sent:** {subscriber['last_sent']}")
                
                # Add delete button
                if st.button(f"🗑️ Delete {subscriber['email']}", key=f"delete_{idx}"):
                    subscribers_df = subscribers_df.drop(index=idx)
                    os.makedirs('data', exist_ok=True)
                    subscribers_df.to_csv("data/email_alert_subscribers.csv", index=False)
                    st.success("✅ Subscriber deleted successfully!")
                    st.rerun()
            
        # Add new subscriber form
        with st.expander("➕ Add New Subscriber", expanded=False):
            with st.form("add_subscriber_form"):
                st.write("### Add New Subscriber")
                new_email = st.text_input("Email")
                new_name = st.text_input("Name")
                new_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
                new_interests = st.multiselect(
                    "Interests",
                    ["New Listings", "Price Drops", "Market Trends", "Project Updates"],
                    default=["New Listings"]
                )
                
                if st.form_submit_button("Add Subscriber"):
                    if new_email and "@" in new_email:
                        # Check if email already exists
                        if new_email in subscribers_df['email'].values:
                            st.warning("This email is already subscribed.")
                        else:
                            # Add new subscriber
                            new_subscriber = pd.DataFrame([{
                                'email': new_email,
                                'name': new_name,
                                'frequency': new_frequency,
                                'interests': ", ".join(new_interests),
                                'subscribed_at': dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'last_sent': '',
                                'status': 'Active'
                            }])
                            
                            # Append to existing data and save
                            subscribers_df = pd.concat([subscribers_df, new_subscriber], ignore_index=True)
                            os.makedirs('data', exist_ok=True)
                            subscribers_df.to_csv("data/email_alert_subscribers.csv", index=False)
                            st.success(f"✅ {new_email} has been added as a subscriber!")
                            st.rerun()
                    else:
                        st.error("Please enter a valid email address.")
                        
        # Bulk Email Section
        st.markdown("### 📧 Send Bulk Email to Subscribers")
        
        # Use a form key that persists between reruns
        form_key = "bulk_email_form"
        
        # Initialize form data in session state if not exists
        if 'email_form_data' not in st.session_state:
            st.session_state.email_form_data = {
                'subject': '',
                'body': """Dear {name},\n\n[Your message here]\n\nBest regards,\nWestProp Team""",
                'status_filter': ["Active"],
                'frequency_filter': ["Weekly"]
            }

        # Show email status if available
        if 'email_sent' in st.session_state and st.session_state.email_sent:
            st.balloons()
            with st.container():
                st.success("✅ Email sent successfully! You can find a copy in your Sent folder.")
                st.balloons()
                
                # Add a button to send another email
                if st.button("✉️ Send Another Email"):
                    del st.session_state.email_sent
                    st.rerun()
                    
                st.markdown("---")
                # Clear the sent status after showing the message
                del st.session_state.email_sent
        else:
            # Show email composition form
            with st.expander("✏️ Compose Email", expanded=True):
                with st.form("email_compose_form"):
                    # Subject and body inputs
                    subject = st.text_input(
                        "Subject", 
                        value=st.session_state.email_form_data['subject'],
                        key="email_subject"
                    )
                    
                    body = st.text_area(
                        "Email Body", 
                        value=st.session_state.email_form_data['body'],
                        key="email_body"
                    )
                    
                    # Filter options
                    st.markdown("**Filters**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        status_options = ["Active", "Paused", "Unsubscribed"]
                        if 'status' in subscribers_df:
                            existing_statuses = [s for s in subscribers_df['status'].dropna().unique().tolist() 
                                              if s and s not in status_options]
                            status_options.extend(existing_statuses)
                        
                        status_filter = st.multiselect(
                            "Status",
                            options=status_options,
                            default=st.session_state.email_form_data['status_filter'],
                            key="status_filter"
                        )
                    
                    with col2:
                        frequency_options = ["Daily", "Weekly", "Monthly"]
                        if 'frequency' in subscribers_df:
                            existing_freqs = [f for f in subscribers_df['frequency'].unique().tolist() 
                                           if f and f not in frequency_options]
                            frequency_options.extend(existing_freqs)
                        
                        frequency_filter = st.multiselect(
                            "Frequency",
                            options=frequency_options,
                            default=st.session_state.email_form_data['frequency_filter'],
                            key="frequency_filter"
                        )
                    
                    # Send button with confirmation
                    if st.form_submit_button("Send Email"):
                        if not st.session_state.get('email_subject') or not st.session_state.get('email_body'):
                            st.error("Please fill in both subject and email body.")
                            st.stop()
                        
                        # Save form data to session state
                        st.session_state.email_form_data = {
                            'subject': st.session_state.email_subject,
                            'body': st.session_state.email_body,
                            'status_filter': st.session_state.get('status_filter', ["Active"]),
                            'frequency_filter': st.session_state.get('frequency_filter', ["Weekly"])
                        }
                        
                        # Filter subscribers based on selected filters
                        filtered_subs = subscribers_df.copy()
                        if st.session_state.email_form_data['status_filter']:
                            filtered_subs = filtered_subs[filtered_subs['status'].isin(st.session_state.email_form_data['status_filter'])]
                        if st.session_state.email_form_data['frequency_filter']:
                            filtered_subs = filtered_subs[filtered_subs['frequency'].isin(st.session_state.email_form_data['frequency_filter'])]
                        
                        if len(filtered_subs) == 0:
                            st.warning("No subscribers match the selected filters.")
                            st.stop()
                        
                        # Send the emails with a spinner
                        with st.spinner(f"Sending emails to {len(filtered_subs)} subscribers..."):
                            from email_service import send_bulk_email
                            success_count, error_count = send_bulk_email(
                                filtered_subs,
                                st.session_state.email_form_data['subject'],
                                st.session_state.email_form_data['body']
                            )
                            
                            if success_count > 0:
                                st.session_state.email_sent = True
                                st.session_state.email_sent_count = success_count
                                st.session_state.email_error_count = error_count
                                st.rerun()
                            elif error_count > 0:
                                st.error(f" Failed to send to all {error_count} subscribers. Please try again.")
            
            # Update the filtered subscribers count in the form
            filtered_subs = subscribers_df.copy()
            if 'status_filter' in st.session_state and st.session_state.status_filter:
                filtered_subs = filtered_subs[filtered_subs['status'].isin(st.session_state.status_filter)]
            if 'frequency_filter' in st.session_state and st.session_state.frequency_filter:
                filtered_subs = filtered_subs[filtered_subs['frequency'].isin(st.session_state.frequency_filter)]
            
            # Update the recipients count in the form
            st.session_state.recipients_count = len(filtered_subs)
        
        # Show email status if available
        if 'email_sent' in st.session_state and st.session_state.email_sent:
            st.balloons()
            with st.container():
                st.success("Email sent successfully! You can find a copy in your Sent folder.")
                st.balloons()
                
                # Add a button to send another email
                if st.button("Send Another Email"):
                    del st.session_state.email_sent
                    st.rerun()
                    
                st.markdown("---")
        
        # Show summary stats
        st.write("### Subscriber Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Subscribers", len(subscribers_df))
            
        with col2:
            active_count = len(subscribers_df[subscribers_df['status'].str.lower() == 'active']) if 'status' in subscribers_df else 0
            st.metric("Active Subscribers", active_count)
            
        with col3:
            st.metric("Last Updated", dt.now().strftime("%Y-%m-%d %H:%M"))
            
        with col4:
            if not subscribers_df.empty and 'frequency' in subscribers_df and not subscribers_df['frequency'].empty:
                freq = subscribers_df['frequency'].mode()[0] if not subscribers_df['frequency'].empty else 'N/A'
            else:
                freq = 'N/A'
            st.metric("Most Common Frequency", freq)
            
            # Make a copy and reset index to avoid MultiIndex issues
            editable_df = subscribers_df.copy().reset_index(drop=True)
            
            # Convert datetime columns to string for editing
            datetime_cols = ['subscribed_at', 'last_sent']
            for col in datetime_cols:
                if col in editable_df.columns:
                    # Convert datetime to string for display
                    if pd.api.types.is_datetime64_any_dtype(editable_df[col]):
                        editable_df[col] = editable_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # If not datetime, ensure it's a string
                        editable_df[col] = editable_df[col].astype(str)
                        
                        # Try to convert to datetime and back to string
                        try:
                            editable_df[col] = pd.to_datetime(editable_df[col], errors='coerce')
                            editable_df[col] = editable_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
            
            # Show data editor for managing subscribers
            edited_df = st.data_editor(
                editable_df,
                column_config={
                    "email": st.column_config.TextColumn(
                        "Email",
                        help="Subscriber's email address",
                        required=True
                    ),
                    "name": st.column_config.TextColumn(
                        "Name",
                        help="Subscriber's name"
                    ),
                    "frequency": st.column_config.SelectboxColumn(
                        "Frequency",
                        help="How often to send updates",
                        options=["Daily", "Weekly", "Monthly"],
                        required=True
                    ),
                    "interests": st.column_config.TextColumn(
                        "Interests",
                        help="Comma-separated list of interests"
                    ),
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        help="Subscription status",
                        options=["Active", "Inactive", "Unsubscribed"],
                        required=True
                    ),
                    "subscribed_at": st.column_config.TextColumn(
                        "Subscribed On",
                        help="Date of subscription"
                    ),
                    "last_sent": st.column_config.TextColumn(
                        "Last Email Sent",
                        help="Date of last email sent"
                    )
                },
                hide_index=True,
                use_container_width=True,
                key="subscribers_editor_advanced"
            )
            
            # Handle saving changes
            if st.button(" Save All Changes"):
                try:
                    # Get edited data
                    edited_data = st.session_state.subscribers_editor_advanced["edited_rows"]
                    
                    # Apply changes to the dataframe
                    for idx, changes in edited_data.items():
                        for col, value in changes.items():
                            editable_df.at[idx, col] = value
                    
                    # Save the changes back to the CSV in the data directory
                    os.makedirs('data', exist_ok=True)
                    editable_df.to_csv("data/email_alert_subscribers.csv", index=False)
                    st.success(" Changes saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f" Error saving changes: {str(e)}")
            
            # Confirmation dialog for sending emails
            if 'pending_email' in st.session_state and st.session_state.pending_email is not None:
                pending = st.session_state.pending_email
                filtered_subs = pending.get('subs', pd.DataFrame())
                email_subject = pending.get('subject', '')
                email_body = pending.get('body', '')
                
                with st.container():
                    st.markdown("---")
                    st.subheader(" Email Confirmation")
                    
                    # Confirmation section
                    st.markdown("###  Confirmation")
                    st.markdown(f"**Recipients:** {len(filtered_subs)} subscribers")
                    
                    # Show a sample of recipients (first 3)
                    if not filtered_subs.empty:
                        sample_recipients = filtered_subs['email'].head(3).tolist()
                        if len(filtered_subs) > 3:
                            sample_recipients.append("...")
                        st.markdown(f"**Sample recipients:**  \n{', '.join(sample_recipients)}")
                        
                    st.markdown("**Sending to:**")
                    if pending.get('filter_type', 'all') == 'all':
                        st.markdown("✅ All subscribers")
                    else:
                        st.markdown(f"✅ {pending.get('filter_type', '').title()} subscribers")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Confirm & Send to {len(filtered_subs)} Subscribers", key=f"confirm_send_{len(filtered_subs)}_{pd.Timestamp.now().value}"):
                        with st.spinner(f"Sending to {len(filtered_subs)} subscribers..."):
                            try:
                                # Initialize progress bar and status text
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                def update_progress(progress, current, total, success, error):
                                    progress_bar.progress(progress)
                                    status_text.text(f"Sending... {current}/{total} ({success} sent, {error} failed)")
                                
                                # Send the emails with a spinner
                                with st.spinner(f"Sending emails to {len(filtered_subs)} subscribers..."):
                                    from email_service import send_bulk_email
                                    success_count, error_count = send_bulk_email(
                                        filtered_subs, 
                                        email_subject, 
                                        email_body,
                                        progress_callback=update_progress
                                    )
                                
                                # Update subscriber last_sent timestamps
                                if not filtered_subs.empty and 'email' in filtered_subs.columns:
                                    subscribers_df.loc[subscribers_df['email'].isin(filtered_subs['email']), 'last_sent'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                                    subscribers_df.to_csv("data/email_alert_subscribers.csv", index=False)
                                
                                # Show success message
                                st.success(f"✅ Successfully sent {success_count} emails!")
                                if error_count > 0:
                                    st.warning(f"⚠️ Failed to send {error_count} emails")
                                
                                # Clear the pending email state
                                del st.session_state.pending_email
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Failed to send emails: {str(e)}")
                
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_send_email_{pd.Timestamp.now().value}"):
                        del st.session_state.pending_email
                        st.rerun()
                
                st.markdown("---")
                st.balloons()
                
                # Clear the pending email after successful send
                if 'pending_email' in st.session_state:
                    del st.session_state.pending_email
                
                # Show success message and refresh
                st.success("✅ Email sent successfully!")
                st.rerun()
            
            st.markdown("### ✉️ Test Email System")
            test_recipient = st.text_input("Recipient Email Address", 
                                        value=st.session_state.get("user_email", ""),
                                        key="test_recipient")
            
            if st.button("✉️ Send Test Email", key="send_test_email"):
                if not test_recipient or "@" not in test_recipient:
                    st.error("Please enter a valid email address")
                else:
                    with st.spinner("Sending test email..."):
                        try:
                            from send_alerts import send_email
                            test_subject = "✅ WestProp Alerts: Test Email"
                            test_body = "This is a test email from the WestProp Alerts system.\n\nIf you received this, the email system is working correctly!"
                            
                            if send_email(test_recipient, test_subject, test_body):
                                st.success(f"✅ Test email sent to {test_recipient}")
                                st.balloons()
                            else:
                                st.error("Failed to send test email. Please check the logs for more details.")
                        except Exception as e:
                            st.error(f"Failed to send test email: {str(e)}")
                            st.error("Please ensure the email service is properly configured with valid credentials.")

def send_bulk_email(recipients_df, subject, body):
    """
    Send bulk emails to a list of recipients
    
    Args:
        recipients_df (DataFrame): DataFrame containing subscriber emails and info
        subject (str): Email subject
        body (str): Email body (can include {name} for personalization)
    """
    import time  # Add this import at the top of the file
    from tqdm import tqdm
    from send_alerts import send_email
    
    success_count = 0
    error_count = 0
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        for i, (_, row) in enumerate(tqdm(recipients_df.iterrows(), total=len(recipients_df))):
            try:
                # Personalize the email
                personalized_body = body
                if '{name}' in body and 'name' in row and pd.notna(row['name']):
                    first_name = row['name'].split(' ')[0]
                    personalized_body = body.replace('{name}', first_name)
                
                # Send the email
                if send_email(
                    recipient=row['email'],
                    subject=subject,
                    body=personalized_body
                ):
                    success_count += 1
                    
                    # Update last_sent timestamp
                    if 'last_sent' in row:
                        recipients_df.at[_, 'last_sent'] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    error_count += 1
                
                # Update progress
                progress = (i + 1) / len(recipients_df)
                progress_bar.progress(progress)
                status_text.text(f"Sending... {i+1}/{len(recipients_df)} ({success_count} sent, {error_count} failed)")
                
                # Small delay to avoid hitting rate limits (using a simple loop instead of time.sleep)
                _ = [i for i in range(1000000)]  # Creates a small delay
                
            except Exception as e:
                error_count += 1
                st.error(f"Error sending to {row.get('email', 'unknown')}: {str(e)}")
        
        # Save updated last_sent timestamps
        if 'last_sent' in recipients_df.columns and not recipients_df.empty:
            # Update the main subscribers dataframe
            subscribers_df.update(recipients_df[['last_sent']])
            subscribers_df.to_csv('email_alert_subscribers.csv', index=False)
        
        # Show completion message
        st.success(f"✅ Email campaign completed! Sent: {success_count}, Failed: {error_count}")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error in bulk email process: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()
        
    # Test email functionality moved to the admin section where it belongs
    # This was previously incorrectly indented code that caused a syntax error
    
    try:
        # This is where the code that might raise an exception would go
        pass
    except Exception as e:
        st.error(f"Error loading subscribers: {str(e)}")
    else:
        st.info("No subscribers found. The subscribers file will be created when someone subscribes.")

    st.info("**No new alerts at this time.** Check back later for updates!")

    st.subheader("Subscribe to Alerts")
    with st.form("alert_subscription_form"):
        alert_email = st.text_input("Email address*")
        alert_frequency = st.selectbox("Alert Frequency*", ["Daily", "Weekly", "Monthly"], index=1)
        interest_areas = st.multiselect("Areas of Interest (select all that apply)",
                                     ["New Listings", "Price Drops", "Special Offers", "Market Updates", "Project Updates"])
        alert_submit = st.form_submit_button("Subscribe")

        if alert_submit:
            if alert_email and "@" in alert_email:
                import csv
                import os
                from datetime import datetime
                
                # Prepare subscription data
                subscription_data = {
                    'email': alert_email,
                    'frequency': alert_frequency,
                    'interests': ','.join(interest_areas) if interest_areas else 'All',
                    'subscribed_at': dt.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    'last_sent': '',
                    'status': 'Active'
                }
                
                # File path for subscriptions
                csv_file = 'email_alert_subscribers.csv'
                file_exists = os.path.isfile(csv_file)
                
                # Check if email already exists
                existing_emails = set()
                if file_exists:
                    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        if reader.fieldnames:
                            existing_emails = {row['email'] for row in reader if row.get('email')}
                
                # Write to CSV
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=subscription_data.keys())
                    if not file_exists:
                        writer.writeheader()
                    if alert_email not in existing_emails:
                        writer.writerow(subscription_data)
                        st.success(f"✅ Successfully subscribed {alert_email} to {alert_frequency} alerts!")
                    else:
                        st.info("ℹ️ You're already subscribed! We'll update your preferences.")
                        
                        # Update existing subscription
                        if file_exists:
                            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                                rows = list(csv.DictReader(f))
                            
                            # Update existing subscription
                            updated = False
                            for row in rows:
                                if row.get('email') == alert_email:
                                    row.update({
                                        'frequency': alert_frequency,
                                        'interests': ','.join(interest_areas) if interest_areas else 'All',
                                        'status': 'Active'
                                    })
                                    updated = True
                                    break
                            
                            # Write updated data back to file
                            if updated:
                                try:
                                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                                        writer = csv.DictWriter(f, fieldnames=subscription_data.keys())
                                        writer.writeheader()
                                        writer.writerows(rows)
                                    st.success("Your subscription preferences have been updated!")
                                except Exception as e:
                                    st.error(f"Error updating subscription: {str(e)}")
                        else:
                            st.error("❌ Please enter a valid email address.")

# --- Community Insights ---
if page == "🏆 Community Insights":
    st.title("🏆 Community Insights & Investor Leaderboard")

    # --- Most Simulated Project ---
    st.subheader("📈 Most Simulated Project")
    if os.path.exists("session_log.csv"):
        log_df = pd.read_csv("session_log.csv")
        if not log_df.empty and "Market Price" in log_df.columns:
            if "Project" in log_df.columns:
                most_sim_project = log_df["Project"].value_counts().idxmax()
                st.metric("Most Simulated Project", most_sim_project)
            else:
                most_sim_price = log_df["Market Price"].mode()[0]
                st.metric("Most Simulated Market Price", f"${most_sim_price:,.0f}")
        else:
            st.info("No simulation data yet.")
    else:
        st.info("No simulation data yet.")

    # --- Top ROI Location (from voting data) ---
    st.subheader("📍 Top ROI Location (by Simulated ROI)")
    if os.path.exists("vote_results.csv"):
        vote_df = pd.read_csv("vote_results.csv")
        if not vote_df.empty and "ROI (%)" in vote_df.columns:
            top_roi = vote_df.loc[vote_df["ROI (%)"].idxmax()]
            st.metric("Top ROI", f"{top_roi['ROI (%)']:.2f}%")
            st.markdown(f"**Project:** {top_roi.get('Project', 'N/A')}  \n**Location:** ({top_roi.get('Latitude', 0):.5f}, {top_roi.get('Longitude', 0):.5f})")
        else:
            st.info("No voting data yet.")
    else:
        st.info("No voting data yet.")

    # --- Investor Sentiment Trends ---
    st.subheader("🗳️ Investor Sentiment Trends")
    if os.path.exists("vote_results.csv"):
        vote_df = pd.read_csv("vote_results.csv")
        if not vote_df.empty and "Vote" in vote_df.columns:
            sentiment = vote_df["Vote"].value_counts(normalize=True) * 100
            yes_pct = sentiment.get("Yes", 0)
            no_pct = sentiment.get("No", 0)
            st.metric("Yes Votes", f"{yes_pct:.1f}%")
            st.metric("No Votes", f"{no_pct:.1f}%")
            # Optional: Pie chart
            fig, ax = plt.subplots()
            ax.pie([yes_pct, no_pct], labels=["Yes", "No"], autopct="%1.1f%%", colors=["#4CAF50", "#F44336"])
            ax.set_title("Investor Sentiment")
            st.pyplot(fig)
        else:
            st.info("No sentiment data yet.")
    else:
        st.info("No sentiment data yet.")

elif page == "📉 Market Trends & Analytics":
    st.title("📉 Market Trends & Analytics")
    st.markdown("Analyze historical market data and forecast future trends.")
    st.caption("Source: Property.co.zw Real Estate Index, 2024")

    # --- National Market Overview ---
    st.subheader("🏠 National Market Overview")
    overview_data = {
        "Property Type": ["All (Avg)", "Commercial", "Flats & Apartments", "Houses", "Land"],
        "Avg Sale Price (USD)": [105000, 425000, 85000, 128000, 55000],
        "Annual Appreciation (%)": [31.2, 6.2, 21.4, 28.0, 22.2],
        "Avg Rent (USD/mo)": [900, 1500, 800, 900, None],
        "Rental Yield (%)": [0.0, 0.0, 6.7, 0.0, 0.0]
    }
    overview_df = pd.DataFrame(overview_data)
    st.dataframe(overview_df)

    # --- Regional Breakdown ---
    st.subheader("🌍 Regional Price & Rent Overview")
    region_data = {
        "Region": [
            "Bulawayo", "Harare", "Manicaland", "Mashonaland Central", "Mashonaland East",
            "Mashonaland West", "Masvingo Province", "Matabeleland North", "Matabeleland South", "Midlands Province"
        ],
        "Avg Sale Price (USD)": [
            100000, 130000, 90000, 95000, 42000, 47500, 90000, 350000, 72500, 60000
        ],
        "Annual Appreciation (%)": [
            9.1, 36.8, 10.0, 58.3, 20.0, 5.6, 110.5, 42.9, 45.0, 33.3
        ],
        "Avg Rent (USD/mo)": [
            800, 1000, 800, 1250, 450, 600, 500, 1310, 1925, 455
        ],
        "Rental Yield (%)": [
            33.3, 5.3, 60.0, 56.2, 0.0, 20.0, 92.3, 74.7, 654.9, 2.2
        ]
    }
    region_df = pd.DataFrame(region_data)
    st.dataframe(region_df)

    # --- Appreciation Bar Chart ---
    st.subheader("📈 Annual Price Appreciation by Region")
    fig, ax = plt.subplots()
    ax.bar(region_df["Region"], region_df["Annual Appreciation (%)"], color="#003366")
    ax.set_ylabel("Appreciation (%)")
    ax.set_title("2024 Annual Price Appreciation")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

    # --- Rental Yield Bar Chart (Flats & Apartments) ---
    st.subheader("🏢 Rental Yields: Flats & Apartments vs. Houses")
    yield_data = {
        "Type": ["Flats & Apartments", "Houses"],
        "Rental Yield (%)": [6.7, 0.0]
    }
    yield_df = pd.DataFrame(yield_data)
    fig2, ax2 = plt.subplots()
    ax2.bar(yield_df["Type"], yield_df["Rental Yield (%)"], color=["#FFC72C", "#4A4A4A"])
    ax2.set_ylabel("Rental Yield (%)")
    ax2.set_title("2024 Rental Yields")
    st.pyplot(fig2)

    # --- Smart Feature Adoption (Sample/Dummy Data) ---
    st.subheader("🔌 Smart Feature Adoption (Sample)")
    st.caption("Estimated % of new builds with solar, water recycling, or smart locks (illustrative).")
    df_sample = pd.DataFrame({
        'Year': [2019, 2020, 2021, 2022, 2023, 2024],
        'Adoption (%)': [5, 8, 12, 18, 25, 33]
    })
    chart = alt.Chart(df_sample).mark_line().encode(
        x=alt.X('Year:O', axis=alt.Axis(format='d')),  # 'd' format for integer years
        y='Adoption (%)'
    )
    st.altair_chart(chart, use_container_width=True)

    # --- Smart Feature Adoption Trends (Zimbabwe Urban New Builds, Estimated) ---
    st.subheader("🔌 Smart Feature Adoption Trends")
    st.caption("Estimated % of new builds with solar, water recycling, and smart locks in Zimbabwe (2019–2024). Sources: World Bank, GreenCape, Coldwell Banker, local developer interviews.")

    # Create a tidy/long-form DataFrame for better Altair compatibility
    years = [2019, 2020, 2021, 2022, 2023, 2024] * 3
    categories = (['Solar (%)'] * 6) + (['Water Recycling (%)'] * 6) + (['Smart Locks (%)'] * 6)
    values = [5, 8, 12, 18, 25, 33, 2, 3, 4, 6, 8, 10, 2, 3, 5, 7, 8, 10]
    
    adoption_df = pd.DataFrame({
        'Year': years,
        'Category': categories,
        'Value': values
    })
    
    # Create the chart with Altair
    chart = alt.Chart(adoption_df).mark_line().encode(
        x=alt.X('Year:O', axis=alt.Axis(format='d', title='Year')),  # 'd' format for integer years
        y=alt.Y('Value', title='Adoption (%)'),
        color='Category',
        tooltip=['Year:O', 'Category', 'Value']
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("--- ")
    st.info("**Note:** This section provides conceptual examples. Real-time market data integration would require access to dynamic data APIs.")

elif page == "🛡️ Admin Analytics":
    st.title("🛡️ Admin Analytics")
    st.markdown("Admin-only access to detailed usage statistics and system insights.")

    # Initialize admin analytics login state if not exists
    if "admin_analytics_logged_in" not in st.session_state:
        st.session_state.admin_analytics_logged_in = False
        st.session_state.admin_logged_in = False  # For backward compatibility

    # Show login form if not logged in
    if not st.session_state.admin_analytics_logged_in:
        with st.form("admin_login_form"):
            st.subheader("Admin Login")
            password = st.text_input("Enter Admin Password", type="password", key="admin_password")
            if st.form_submit_button("Login"):
                if password == "westprop2025":
                    st.session_state.admin_analytics_logged_in = True
                    st.session_state.admin_logged_in = True  # For backward compatibility
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")
        st.stop()  # Stop execution here if not logged in
    
    # Only show this content if logged in
    st.subheader("Session Log Analysis")
    try:
        session_df = pd.read_csv("session_log.csv")
        st.write(f"Total Simulations Recorded: {len(session_df)}")
        st.dataframe(session_df)

        st.subheader("Key Metrics from Simulations")
        avg_market_price = session_df["Market Price"].mean()
        avg_monthly_rent = session_df["Monthly Rent"].mean()
        avg_predicted_roi = session_df["Predicted ROI (Model)"].mean()
        avg_smart_roi = session_df["Smart ROI (Calculated)"].mean()

        st.write(f"Average Market Price Simulated: ${avg_market_price:,.2f}")
        st.write(f"Average Monthly Rent Simulated: ${avg_monthly_rent:,.2f}")
        st.write(f"Average Predicted ROI (Model): {avg_predicted_roi:.2f}%")
        st.write(f"Average Smart ROI (Calculated): {avg_smart_roi:.2f}%")

        st.subheader("Smart Feature Usage")
        smart_feature_cols = [
            "Has Solar", "Has Water Recycling", "Has Smart Locks",
            "Has Smart Thermostats", "Has Integrated Security", "Has EV Charging"
        ]
        usage_data = {}
        for col in smart_feature_cols:
            if col in session_df.columns:
                usage_data[col] = session_df[col].sum()
        
        if usage_data:
            usage_df = pd.DataFrame(usage_data.items(), columns=["Smart Feature", "Times Used"])
            st.dataframe(usage_df.sort_values(by="Times Used", ascending=False))
        else:
            st.info("No smart feature usage data available.")
    except FileNotFoundError:
        st.warning("No session log data found.")
    except Exception as e:
        st.error(f"An error occurred during admin analytics: {e}")
    if st.button("Logout Admin", key="admin_logout_btn"):
        # Clear all admin-related session state
        st.session_state.admin_analytics_logged_in = False
        st.session_state.admin_logged_in = False
        # Clear any navigation flags
        if 'go_to_roi_map' in st.session_state:
            del st.session_state['go_to_roi_map']
            
        # Show logout message
        st.success("Successfully logged out!")
        # Force a rerun to update the UI
        st.rerun()



