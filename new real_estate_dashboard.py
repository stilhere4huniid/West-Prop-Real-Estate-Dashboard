import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
import datetime
import os
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import joblib # For loading trained model and transformer
from io import BytesIO # For PDF generation
from reportlab.lib.pagesizes import A4 # For PDF generation
from reportlab.pdfgen import canvas # For PDF generation
from reportlab.lib.utils import ImageReader # For PDF generation
import io # For PDF generation
import json # For handling JSON data
from datetime import datetime # For timestamps
import smtplib # For email functionality
from email.message import EmailMessage # For email functionality
import numpy as np # For numerical operations, especially with dummy coordinates
from dotenv import load_dotenv # For loading environment variables (e.g., email credentials)
import seaborn as sns # For enhanced plots in Executive Summary

# Load environment variables from .env file
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Load smart feature value proposition table (from original dashboard)
smart_value_df = pd.read_csv("data/smart_feature_value_table.csv")

# --- CONFIG ---
st.set_page_config(page_title="Smart Real Estate ROI Simulator", layout="centered")
st.image("westprop_logo.png", width=200)

# Load the trained model, transformer, and feature names
# Assuming these files are in the same directory as the dashboard script
model = joblib.load("models/roi_prediction_model.pkl")
pt = joblib.load("models/roi_transformer.pkl") # PowerTransformer for inverse transformation
model_features = joblib.load("models/model_features.pkl") # List of features the model was trained on

# Load the real estate data template with all calculated ROIs
real_estate_df = pd.read_csv("data/real_estate_data_template.csv")

# --- Smart Feature Savings (Updated based on research) ---
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

# Convert to DataFrame for easier filtering
properties_df = pd.DataFrame(properties_data)

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
        "description": "Zimbabwe\"s first integrated luxury golf estate offering villas and residential stands. Features include golf access, mall access, wellness center, and high security.",
        "url": "https://www.westprop.com/developments/the-hills/"
    },
    "Radisson Serviced Apartments": {
        "image": "project_images/radisson_apartments.webp", # Adjusted path
        "description": "Luxury serviced apartments managed by Radisson, available through the Seatrite 5 REIT. Offers hotel services, pool, gym, and conference facilities with guaranteed returns.",
        "url": "https://www.westprop.com/developments/millenium-serviced-apartments/" # Note: Link might be broken
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
    "❓ Help", "ℹ️ About", "🔔 Alerts", "🏆 Community Insights", "📉 Market Trends & Analytics"
]
if st.session_state.get("admin_logged_in", False):
    pages.append("🛡️ Admin Analytics")

page = st.sidebar.radio("Go to", pages, key="page")

# --- Simulator Page ---
if page == "🏠 Simulator":
    st.title("🏡 Smart Real Estate ROI Simulator")
    st.markdown("Simulate the ROI impact of adding smart features to your property.")

    with st.sidebar.form("simulator_form"):
        st.header("⚙️ Simulate Your Property")
        market_price = st.number_input(
            "Market Price (USD)",
            value=st.session_state.market_price,
            step=1000,
            help="Enter the estimated property sale price."
        )
        monthly_rent = st.number_input(
            "Expected Monthly Rent (USD)",
            value=st.session_state.monthly_rent,
            step=50,
            help="Enter the expected rent you’ll charge monthly."
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
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        file_path = "session_log.csv"
        snapshot_df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)

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

    st.subheader("📊 ROI Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Traditional ROI (Net)", f"{roi:.2f} %")
    col2.metric("Smart ROI (Net)", f"{smart_roi:.2f} %")
    col3.metric("Predicted ROI (Model)", f"{predicted_roi_original:.2f} %")

    st.markdown("### 💸 Estimated Annual & Lifetime Savings")
    st.write(f"**Annual Savings from Smart Features:** ${annual_savings_total:.2f}")
    st.write(f"**Lifetime Savings (5 Years):** ${annual_savings_total * 5:.2f}")
    st.write(f"**Lifetime Savings (10 Years):** ${annual_savings_total * 10:.2f}")

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
    
    # Sliders for all 6 smart feature adoption percentages
    solar_adopt = st.slider("Solar Adoption (%)", 0, 100, 100 if st.session_state.has_solar else 0, step=10)
    water_recycling_adopt = st.slider("Water Recycling Adoption (%)", 0, 100, 100 if st.session_state.has_water_recycling else 0, step=10)
    smart_locks_adopt = st.slider("Smart Locks Adoption (%)", 0, 100, 100 if st.session_state.has_smart_locks else 0, step=10)
    smart_thermostats_adopt = st.slider("Smart Thermostats Adoption (%)", 0, 100, 100 if st.session_state.has_smart_thermostats else 0, step=10)
    integrated_security_adopt = st.slider("Integrated Security Adoption (%)", 0, 100, 100 if st.session_state.has_integrated_security else 0, step=10)
    ev_charging_adopt = st.slider("EV Charging Adoption (%)", 0, 100, 100 if st.session_state.has_ev_charging else 0, step=10)

    base_price = st.session_state.market_price
    base_rent = st.session_state.monthly_rent

    # Updated ROI calculation to use adoption percentages and full expense model
    def calc_roi_with_expenses(price, rent, solar_pct, water_recycling_pct, smart_locks_pct, smart_thermostats_pct, integrated_security_pct, ev_charging_pct):
        annual_rent = rent * 12

        # Expense rates (from initial setup)
        PROPERTY_TAX_RATE = 0.01
        MAINTENANCE_RATE = 0.015
        INSURANCE_RATE = 0.004
        AGENT_FEE_RATE = 0.10

        annual_property_tax_usd = price * PROPERTY_TAX_RATE
        annual_maintenance_usd = price * MAINTENANCE_RATE
        annual_insurance_usd = price * INSURANCE_RATE
        annual_agent_fees_usd = annual_rent * AGENT_FEE_RATE
        total_annual_expenses_usd = annual_property_tax_usd + annual_maintenance_usd + annual_insurance_usd + annual_agent_fees_usd

        # Calculate smart savings based on adoption percentages
        monthly_savings_total = (
            (SOLAR_SAVINGS * (solar_pct / 100))
            + (WATER_RECYCLING_SAVINGS * (water_recycling_pct / 100))
            + (SMART_LOCKS_SAVINGS * (smart_locks_pct / 100))
            + (SMART_THERMOSTATS_SAVINGS * (smart_thermostats_pct / 100))
            + (INTEGRATED_SECURITY_SAVINGS * (integrated_security_pct / 100))
            + (EV_CHARGING_SAVINGS * (ev_charging_pct / 100))
        )
        annual_savings_total = monthly_savings_total * 12

        net_annual_income_with_smart_savings = (annual_rent + annual_savings_total) - total_annual_expenses_usd
        return (net_annual_income_with_smart_savings / price) * 100 if price > 0 else 0

    mode = st.radio(
        "Tornado Chart Mode",
        ["Full Impact (0%→100%)", "What-If (Current→100%)"],
        index=0,
        help="Choose whether to see the full possible impact of each feature, or the impact from your current scenario."
    )

    # Define the current state of smart features for What-If scenario
    current_solar_pct = 100 if st.session_state.has_solar else 0
    current_water_recycling_pct = 100 if st.session_state.has_water_recycling else 0
    current_smart_locks_pct = 100 if st.session_state.has_smart_locks else 0
    current_smart_thermostats_pct = 100 if st.session_state.has_smart_thermostats else 0
    current_integrated_security_pct = 100 if st.session_state.has_integrated_security else 0
    current_ev_charging_pct = 100 if st.session_state.has_ev_charging else 0

    if mode == "Full Impact (0%→100%)":
        sensitivity = {
            "Monthly Rent": [
                calc_roi_with_expenses(base_price, rent_range[0], current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, rent_range[1], current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Market Price": [
                calc_roi_with_expenses(price_range[0], base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(price_range[1], base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Solar Adoption": [
                calc_roi_with_expenses(base_price, base_rent, 0, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, 100, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Water Recycling": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, 0, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, 100, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Smart Locks": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, 0, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, 100, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Smart Thermostats": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, 0, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, 100, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Integrated Security": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, 0, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, 100, current_ev_charging_pct)
            ],
            "EV Charging": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, 100)
            ]
        }
    else:  # What-If (Current→100%)
        sensitivity = {
            "Monthly Rent": [
                calc_roi_with_expenses(base_price, rent_range[0], current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, rent_range[1], current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Market Price": [
                calc_roi_with_expenses(price_range[0], base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(price_range[1], base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Solar Adoption": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, 100, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Water Recycling": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, 100, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Smart Locks": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, 100, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Smart Thermostats": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, 100, current_integrated_security_pct, current_ev_charging_pct)
            ],
            "Integrated Security": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, 100, current_ev_charging_pct)
            ],
            "EV Charging": [
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, current_ev_charging_pct),
                calc_roi_with_expenses(base_price, base_rent, current_solar_pct, current_water_recycling_pct, current_smart_locks_pct, current_smart_thermostats_pct, current_integrated_security_pct, 100)
            ]
        }

    labels = []
    impacts = []
    for k, v in sensitivity.items():
        delta = abs(v[1] - v[0])
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
    selected_project_option = st.selectbox(
        "Choose a Project & Unit Type (optional):",
        options=["(Manual Entry)"] + project_options,
        index=0,
        help="Select a project/unit to auto-fill price, rent, and features. Or use manual entry."
    )

    # If a project is selected, auto-fill session state
    if selected_project_option != "(Manual Entry)":
        selected_idx = project_options.index(selected_project_option)
        selected_row = properties_df.iloc[selected_idx]
        # Example default rents for each property type (customize as needed)
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
            "Flat": 800 # Added for Pomona City Flat
        }
        st.session_state.market_price = selected_row["price"]
        st.session_state.monthly_rent = default_rents.get(selected_row["property_type"], 1000)
        
        # Update all smart features based on amenities
        amenities_list = selected_row["amenities"] or []
        st.session_state.has_solar = "Solar" in amenities_list
        st.session_state.has_water_recycling = "Water Recycling" in amenities_list
        st.session_state.has_smart_locks = "Smart Locks" in amenities_list or "Lock-up Shell" in amenities_list # Consider both terms
        st.session_state.has_smart_thermostats = "Smart Thermostats" in amenities_list
        st.session_state.has_integrated_security = "Integrated Security" in amenities_list
        st.session_state.has_ev_charging = "EV Charging" in amenities_list

        st.info(f"Auto-filled values for {selected_project_option}. You can adjust them below.")




elif page == "🗂️ My Simulations":
    st.title("🗂️ My Saved Simulations")
    st.markdown("Review and manage your past ROI simulations.")

    file_path = "session_log.csv"
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
                st.experimental_rerun()
        else:
            st.info("No simulations saved yet. Run a simulation on the \'Simulator\' page!")
    else:
        st.info("No simulations saved yet. Run a simulation on the \'Simulator\' page!")




elif page == "📈 Executive Summary":
    st.title("📈 Executive Summary")
    st.markdown("A high-level overview of key insights and performance metrics.")

    # 1. Overall ROI Distribution
    st.subheader("1. Overall ROI Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(real_estate_df["ROI_percentage"].dropna(), kde=True, ax=ax, color="skyblue")
    ax.set_title("Distribution of ROI Percentages Across Properties")
    ax.set_xlabel("ROI Percentage")
    ax.set_ylabel("Number of Properties")
    st.pyplot(fig)

    st.write("**Key Takeaway:** This histogram shows the spread of ROI percentages across all properties. A higher concentration towards the right indicates more profitable properties.")

    # 2. Average ROI by Location Suburb
    st.subheader("2. Average ROI by Location Suburb")
    avg_roi_by_suburb = real_estate_df.groupby("location_suburb")["ROI_percentage"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(x=avg_roi_by_suburb.index, y=avg_roi_by_suburb.values, ax=ax, palette="viridis")
    ax.set_title("Average ROI by Location Suburb")
    ax.set_xlabel("Location Suburb")
    ax.set_ylabel("Average ROI Percentage")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

    st.write("**Key Takeaway:** This chart highlights which suburbs tend to offer higher average ROIs, guiding investment decisions based on location.")

    # 3. Average ROI by Property Type
    st.subheader("3. Average ROI by Property Type")
    avg_roi_by_type = real_estate_df.groupby("property_type")["ROI_percentage"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=avg_roi_by_type.index, y=avg_roi_by_type.values, ax=ax, palette="magma")
    ax.set_title("Average ROI by Property Type")
    ax.set_xlabel("Property Type")
    ax.set_ylabel("Average ROI Percentage")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

    st.write("**Key Takeaway:** Different property types yield varying returns. This chart helps identify the most profitable property categories.")

    # 4. Impact of Smart Features on ROI (Conceptual/Model-based)
    st.subheader("4. Impact of Smart Features on ROI")
    st.markdown("The machine learning model has learned the impact of smart features on ROI. While direct comparison on historical data is complex, the model\"s predictions reflect their value.")
    
    # Example: Average ROI for properties with/without solar (if data allows)
    # This requires filtering real_estate_df based on smart features
    if "has_solar" in real_estate_df.columns:
        solar_roi = real_estate_df.groupby("has_solar")["ROI_percentage"].mean()
        if len(solar_roi) > 1:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(x=solar_roi.index, y=solar_roi.values, ax=ax, palette="pastel")
            ax.set_title("Average ROI: Properties With vs. Without Solar")
            ax.set_xlabel("Has Solar (0=No, 1=Yes)")
            ax.set_ylabel("Average ROI Percentage")
            st.pyplot(fig)
            st.write("**Key Takeaway:** Properties with solar tend to have a higher average ROI, reflecting energy savings and increased property value.")
        else:
            st.info("Not enough data to compare ROI for properties with/without solar.")
    else:
        st.info("Smart feature data (e.g., \"has_solar\") not available in the dataset for direct comparison.")

    st.write("**Further Analysis:** The simulator page uses the trained model to predict ROI based on selected smart features, providing a forward-looking view.")

    # 5. Top 5 Properties by ROI
    st.subheader("5. Top 5 Properties by ROI")
    top_5_roi = real_estate_df.sort_values(by="ROI_percentage", ascending=False).head(5)
    st.dataframe(top_5_roi[["property_id", "location_suburb", "property_type", "ROI_percentage", "sale_price_usd", "rental_income_usd_monthly (est)"]])
    st.write("**Key Takeaway:** These are the properties with the highest calculated ROIs in your dataset, representing potentially strong investment opportunities.")

    # --- Dynamic PDF Generation ---
    def generate_pdf(market_price, monthly_rent, has_solar, has_water_recycling, has_smart_locks,
                     has_smart_thermostats, has_integrated_security, has_ev_charging,
                     traditional_roi, smart_roi, predicted_roi_model, annual_savings_total,
                     annual_rent, annual_property_tax_usd, annual_maintenance_usd,
                     annual_insurance_usd, annual_agent_fees_usd, total_annual_expenses_usd,
                     net_annual_income_usd, net_annual_income_with_smart_savings, roi_chart_buf):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        try:
            c.drawImage("westprop_logo.png", 40, 750, width=120, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error loading logo: {e}")
            pass

        text = c.beginText(40, 720)
        text.setFont("Helvetica-Bold", 14)
        text.textLine("WestProp Smart Real Estate ROI Summary")
        text.setFont("Helvetica", 11)
        text.textLine("")
        text.textLine("This one-pager summarizes the current simulation, highlighting ROI and savings.")
        text.textLine("It aligns with WestProp\"s vision for smart & sustainable developments.")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Current Simulation Inputs:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Market Price: ${market_price:,.2f}")
        text.textLine(f"- Monthly Rent: ${monthly_rent:,.2f}")
        text.textLine(f"- Has Solar: {'Yes' if has_solar else 'No'}")
        text.textLine(f"- Has Water Recycling: {'Yes' if has_water_recycling else 'No'}")
        text.textLine(f"- Has Smart Locks: {'Yes' if has_smart_locks else 'No'}")
        text.textLine(f"- Has Smart Thermostats: {'Yes' if has_smart_thermostats else 'No'}")
        text.textLine(f"- Has Integrated Security: {'Yes' if has_integrated_security else 'No'}")
        text.textLine(f"- Has EV Charging: {'Yes' if has_ev_charging else 'No'}")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("ROI Results:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Traditional ROI (Net): {traditional_roi:.2f}%")
        text.textLine(f"- Smart ROI (Net): {smart_roi:.2f}%")
        text.textLine(f"- Predicted ROI (Model): {predicted_roi_model:.2f}%")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Estimated Annual & Lifetime Savings:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Annual Savings from Smart Features: ${annual_savings_total:,.2f}")
        text.textLine(f"- Lifetime Savings (5 Years): ${annual_savings_total * 5:,.2f}")
        text.textLine(f"- Lifetime Savings (10 Years): ${annual_savings_total * 10:,.2f}")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Financial Breakdown:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Annual Rental Income: ${annual_rent:,.2f}")
        text.textLine(f"- Annual Property Tax: ${annual_property_tax_usd:,.2f}")
        text.textLine(f"- Annual Maintenance: ${annual_maintenance_usd:,.2f}")
        text.textLine(f"- Annual Insurance: ${annual_insurance_usd:,.2f}")
        text.textLine(f"- Annual Agent Fees: ${annual_agent_fees_usd:,.2f}")
        text.textLine(f"- Total Annual Expenses: ${total_annual_expenses_usd:,.2f}")
        text.textLine(f"- Net Annual Income (before smart savings): ${net_annual_income_usd:,.2f}")
        text.textLine(f"- Net Annual Income (with smart savings): ${net_annual_income_with_smart_savings:,.2f}")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Interpretation:")
        text.setFont("Helvetica", 11)
        text.textLine("The Predicted ROI (Model) incorporates the impact of all selected features,")
        text.textLine("including smart features, as learned by the machine learning model.")
        text.textLine("The Smart ROI (Net) explicitly adds estimated monthly savings from smart features.")
        text.textLine("This dashboard helps validate pricing, investor returns, and green value.")
        text.textLine("")

        text.setFont("Helvetica-Oblique", 10)
        text.textLine("*This is an auto-generated summary using real-time inputs. All values are estimates.*")
        
        c.drawText(text)

        # --- Draw the ROI chart image ---
        # The chart buffer is generated in the Simulator page, so it should be available in session_state
        if roi_chart_buf:
            try:
                # Ensure the buffer is at the beginning before reading
                roi_chart_buf.seek(0)
                img = ImageReader(roi_chart_buf)
                # Adjust position and size as needed
                c.drawImage(img, 60, 200, width=400, height=220, preserveAspectRatio=True)
            except Exception as e:
                print(f"Error drawing chart image: {e}")
        else:
            c.drawString(60, 250, "ROI Chart not available. Please run a simulation first.")


        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # Ensure all necessary values are available from session state or calculated for the PDF
    # These values should be available from the Simulator page\"s calculations
    # If not, they need to be recalculated here or passed from the Simulator page
    # For simplicity, assuming they are available in st.session_state or as local variables
    # from the Simulator page\"s last run.
    
    # Recalculate for PDF generation if not already in session state (or to ensure fresh values)
    # This recalculation is for the PDF/Email ONLY, not for the main Executive Summary display
    annual_rent_pdf = st.session_state.monthly_rent * 12
    
    PROPERTY_TAX_RATE_PDF = 0.01
    MAINTENANCE_RATE_PDF = 0.015
    INSURANCE_RATE_PDF = 0.004
    AGENT_FEE_RATE_PDF = 0.10

    annual_property_tax_usd_pdf = st.session_state.market_price * PROPERTY_TAX_RATE_PDF
    annual_maintenance_usd_pdf = st.session_state.market_price * MAINTENANCE_RATE_PDF
    annual_insurance_usd_pdf = st.session_state.market_price * INSURANCE_RATE_PDF
    annual_agent_fees_usd_pdf = annual_rent_pdf * AGENT_FEE_RATE_PDF

    total_annual_expenses_usd_pdf = annual_property_tax_usd_pdf + annual_maintenance_usd_pdf + annual_insurance_usd_pdf + annual_agent_fees_usd_pdf
    net_annual_income_usd_pdf = annual_rent_pdf - total_annual_expenses_usd_pdf

    monthly_savings_total_pdf = (
        (SOLAR_SAVINGS if st.session_state.has_solar else 0)
        + (WATER_RECYCLING_SAVINGS if st.session_state.has_water_recycling else 0)
        + (SMART_LOCKS_SAVINGS if st.session_state.has_smart_locks else 0)
        + (SMART_THERMOSTATS_SAVINGS if st.session_state.has_smart_thermostats else 0)
        + (INTEGRATED_SECURITY_SAVINGS if st.session_state.has_integrated_security else 0)
        + (EV_CHARGING_SAVINGS if st.session_state.has_ev_charging else 0)
    )
    annual_savings_total_pdf = monthly_savings_total_pdf * 12

    net_annual_income_with_smart_savings_pdf = (annual_rent_pdf + annual_savings_total_pdf) - total_annual_expenses_usd_pdf
    
    # These ROI values should be directly from the Simulator\"s last run and stored in session_state
    # Assuming they are available as st.session_state.predicted_roi_original, st.session_state.roi, st.session_state.smart_roi
    # If not, you\"d need to re-run the model prediction here for the PDF, which is less efficient.
    # It\"s better to ensure the Simulator page stores these in session_state.
    
    # For the purpose of this update, I will use the session state values that are set
    # by the Simulator page. If the Simulator page hasn\"t been run, these might be default/initial values.
    
    # The chart buffer is also assumed to be in session_state from the Simulator page.
    
    pdf_data = generate_pdf(
        st.session_state.market_price,
        st.session_state.monthly_rent,
        st.session_state.has_solar,
        st.session_state.has_water_recycling,
        st.session_state.has_smart_locks,
        st.session_state.has_smart_thermostats,
        st.session_state.has_integrated_security,
        st.session_state.has_ev_charging,
        st.session_state.roi, # Traditional ROI (Net)
        st.session_state.smart_roi, # Smart ROI (Net)
        st.session_state.predicted_roi_original, # Predicted ROI (Model)
        annual_savings_total_pdf, # Annual savings from smart features
        annual_rent_pdf,
        annual_property_tax_usd_pdf,
        annual_maintenance_usd_pdf,
        annual_insurance_usd_pdf,
        annual_agent_fees_usd_pdf,
        total_annual_expenses_usd_pdf,
        net_annual_income_usd_pdf,
        net_annual_income_with_smart_savings_pdf,
        st.session_state.get('roi_chart_buf', None) # Pass the chart buffer
    )

    st.download_button(
        label="📄 Download Full One-Pager PDF",
        data=pdf_data,
        file_name="WestProp_Smart_ROI_Summary.pdf",
        mime="application/pdf"
    )

    # --- CSV Download ---
    summary_df = pd.DataFrame({
        "Metric": [
            "Traditional ROI (Net)", "Smart ROI (Net)", "Predicted ROI (Model)",
            "Annual Savings from Smart Features", "5-Year Savings", "10-Year Savings",
            "Annual Rental Income", "Annual Property Tax", "Annual Maintenance",
            "Annual Insurance", "Annual Agent Fees", "Total Annual Expenses",
            "Net Annual Income (before smart savings)", "Net Annual Income (with smart savings)"
        ],
        "Value": [
            st.session_state.roi,
            st.session_state.smart_roi,
            st.session_state.predicted_roi_original,
            annual_savings_total_pdf,
            annual_savings_total_pdf * 5,
            annual_savings_total_pdf * 10,
            annual_rent_pdf,
            annual_property_tax_usd_pdf,
            annual_maintenance_usd_pdf,
            annual_insurance_usd_pdf,
            annual_agent_fees_usd_pdf,
            total_annual_expenses_usd_pdf,
            net_annual_income_usd_pdf,
            net_annual_income_with_smart_savings_pdf
        ]
    })

    csv = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📊 Download ROI Summary (CSV)",
        data=csv,
        file_name="roi_summary.csv",
        mime="text/csv"
    )

    # --- EMAIL SUMMARY FEATURE (ONLY IN EXECUTIVE SUMMARY TAB) ---
    st.markdown("### 📧 Email Your Executive Summary")
    email_address = st.text_input("Enter your email address to receive the summary (PDF & CSV):")
    if st.button("Send Summary to Email"):
        if email_address:
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
            except Exception as e:
                st.error(f"Failed to send email: {e}")
        else:
            st.warning("Please enter a valid email address.")




elif page == "🗺️ ROI Map":
    st.title("🗺️ Property ROI Map")
    st.markdown("Visualize properties across Harare with color-coded ROI percentages.")

    # Filter out properties with missing ROI or coordinates for mapping
    map_df = real_estate_df.dropna(subset=["latitude", "longitude", "ROI_percentage"]).copy()

    if not map_df.empty:
        # Center map on Harare (approximate coordinates)
        harare_lat, harare_lon = -17.8251, 31.0335
        m = folium.Map(location=[harare_lat, harare_lon], zoom_start=12)

        # Add a TileLayer for better context (e.g., OpenStreetMap)
        folium.TileLayer("OpenStreetMap").add_to(m)

        # Normalize ROI for color mapping (0 to 1)
        min_roi = map_df["ROI_percentage"].min()
        max_roi = map_df["ROI_percentage"].max()

        def get_color(roi):
            if pd.isna(roi): return "gray"
            # Scale ROI to a 0-1 range
            scaled_roi = (roi - min_roi) / (max_roi - min_roi) if (max_roi - min_roi) != 0 else 0.5
            # Use a color gradient from red (low ROI) to green (high ROI)
            # This is a simple linear interpolation for demonstration
            r = min(255, int(255 * (1 - scaled_roi)))
            g = min(255, int(255 * scaled_roi))
            b = 0
            return f"#{r:02x}{g:02x}{b:02x}"

        # Add markers for each property
        for idx, row in map_df.iterrows():
            popup_html = f"""
            <b>Property ID:</b> {row["property_id"]}<br>
            <b>Suburb:</b> {row["location_suburb"]}<br>
            <b>Type:</b> {row["property_type"]}<br>
            <b>Sale Price:</b> ${row["sale_price_usd"]:,}<br>
            <b>Est. Monthly Rent:</b> ${row["rental_income_usd_monthly (est)"]:,}<br>
            <b>ROI:</b> {row["ROI_percentage"]:.2f}%
            """
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=8,
                color=get_color(row["ROI_percentage"]),
                fill=True,
                fill_color=get_color(row["ROI_percentage"]),
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

        # Heatmap layer (using ROI_percentage as weight)
        heat_data = [[row["latitude"], row["longitude"], row["ROI_percentage"]] for _, row in map_df.iterrows()]
        HeatMap(heat_data, radius=15).add_to(m)

        map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

        # === MAP CLICK EVENT + VOTING SECTION ===
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]

            # Find the closest property in real_estate_df to the clicked location
            # This is a simplified approach; for production, consider spatial indexing
            distances = np.sqrt((map_df["latitude"] - lat)**2 + (map_df["longitude"] - lon)**2)
            closest_idx = distances.idxmin()
            clicked_property = map_df.loc[closest_idx]

            st.markdown(f"📍 **You clicked:** `{lat:.5f}, {lon:.5f}`")
            st.markdown(f"🏢 **Closest Property Detected:** `{clicked_property['property_id']} - {clicked_property['location_suburb']}`")
            st.markdown(f"💡 **Calculated ROI for this property:** `{clicked_property['ROI_percentage']:.2f}%`")

            st.subheader("🗳️ Would You Invest in This Location?")
            vote = st.radio("Your Vote", ["Yes", "No"], horizontal=True, help="Would you consider investing in a property at this location?")

            if st.button("Submit Vote"):
                vote_record = pd.DataFrame([{
                    "Property ID": clicked_property["property_id"],
                    "Latitude": lat,
                    "Longitude": lon,
                    "ROI (%)": round(clicked_property["ROI_percentage"], 2),
                    "Vote": vote,
                    "Timestamp":datetime.now().isoformat()
                }])

                try:
                    existing_votes = pd.read_csv("vote_results.csv")
                    vote_data = pd.concat([existing_votes, vote_record], ignore_index=True)
                except FileNotFoundError:
                    vote_data = vote_record

                vote_data.to_csv("vote_results.csv", index=False)
                st.success("✅ Your vote has been recorded for this property!")
        
        if "admin_logged_in" not in st.session_state:
            st.session_state.admin_logged_in = False

        if not st.session_state.admin_logged_in:
            with st.form("admin_login_form"):
                password_input = st.text_input("Enter admin password to access secure voting data:", type="password")
                submit_login = st.form_submit_button("Login as Admin")

                if submit_login:
                    if password_input == "westprop2025":
                        st.session_state.admin_logged_in = True
                        st.success("✅ Admin access granted")
                    else:
                        st.error("Incorrect password. Try again.")


        if st.session_state.admin_logged_in:
            st.subheader("🔒 Admin Panel — Recent Voting Data")
            try:
                recent_votes = pd.read_csv("vote_results.csv")
                st.dataframe(recent_votes.tail(10))      
            except:
                st.warning("No votes recorded yet.")

            if st.button("🧹 Reset All Votes"):
                with open("vote_results.csv", "w") as f:
                    f.write("Property ID,Latitude,Longitude,ROI (%),Vote,Timestamp\n")
                st.success("🗳️ All votes cleared. Voting restarted fresh.")        
        
        if st.button("🔓 Logout"):
            st.session_state.admin_logged_in = False
            st.session_state.go_to_roi_map = True
            st.info("Logged out.")
            st.rerun()

        # === Optional Vote Summary Chart ===
        if st.session_state.get("admin_logged_in", False):
            st.subheader("📊 Vote Summary by Property ID")
        
            try:
                vote_df = pd.read_csv("vote_results.csv")
                if vote_df.empty:
                    st.info("No votes yet. Chart will appear once votes are recorded.")
                else:
                    # Count Yes/No votes per property ID
                    vote_counts = vote_df.groupby(["Property ID", "Vote"]).size().unstack(fill_value=0)
                    if "Yes" not in vote_counts.columns:
                        vote_counts["Yes"] = 0
                    if "No" not in vote_counts.columns:
                        vote_counts["No"] = 0
                    vote_counts = vote_counts[["Yes", "No"]]

                    # Plot as grouped bar chart
                    fig, ax = plt.subplots(figsize=(8, 5))
                    vote_counts[["Yes", "No"]].plot(kind="bar", ax=ax, color=["#4CAF50", "#F44336"])
                    ax.set_title("Would You Invest? — Votes per Property")
                    ax.set_ylabel("Number of Votes")
                    ax.set_xlabel("Property ID")
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
            except pd.errors.EmptyDataError:            st.info("Voting file is empty. No votes have been recorded yet.")   
            except Exception as e:
                st.error(f"An error occurred while generating the chart: {e}")
    else:
        st.warning("No properties with complete ROI and coordinate data available for mapping.")




elif page == "🔍 Property Browser":
    st.title("🔍 Property Browser")
    st.markdown("Browse and filter the comprehensive real estate dataset.")

    # Filters
    st.sidebar.header("Property Filters")
    selected_suburbs = st.sidebar.multiselect(
        "Select Suburb(s)",
        real_estate_df["location_suburb"].unique(),
        default=[]
    )
    selected_property_types = st.sidebar.multiselect(
        "Select Property Type(s)",
        real_estate_df["property_type"].unique(),
        default=[]
    )
    min_price, max_price = st.sidebar.slider(
        "Sale Price Range (USD)",
        min_value=int(real_estate_df["sale_price_usd"].min()),
        max_value=int(real_estate_df["sale_price_usd"].max()),
        value=(int(real_estate_df["sale_price_usd"].min()), int(real_estate_df["sale_price_usd"].max()))
    )
    min_roi, max_roi = st.sidebar.slider(
        "ROI Percentage Range",
        min_value=float(real_estate_df["ROI_percentage"].min()),
        max_value=float(real_estate_df["ROI_percentage"].max()),
        value=(float(real_estate_df["ROI_percentage"].min()), float(real_estate_df["ROI_percentage"].max()))
    )

    filtered_real_estate_df = real_estate_df.copy()

    if selected_suburbs:
        filtered_real_estate_df = filtered_real_estate_df[
            filtered_real_estate_df["location_suburb"].isin(selected_suburbs)
        ]
    if selected_property_types:
        filtered_real_estate_df = filtered_real_estate_df[
            filtered_real_estate_df["property_type"].isin(selected_property_types)
        ]
    filtered_real_estate_df = filtered_real_estate_df[
        (filtered_real_estate_df["sale_price_usd"] >= min_price) &
        (filtered_real_estate_df["sale_price_usd"] <= max_price)
    ]
    filtered_real_estate_df = filtered_real_estate_df[
        (filtered_real_estate_df["ROI_percentage"] >= min_roi) &
        (filtered_real_estate_df["ROI_percentage"] <= max_roi)
    ]

    st.write(f"Displaying {len(filtered_real_estate_df)} of {len(real_estate_df)} properties.")
    st.dataframe(filtered_real_estate_df)

    st.subheader("Download Filtered Data")
    csv_data = filtered_real_estate_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_real_estate_data.csv",
        mime="text/csv",
    )




elif page == "📍 Project Profiles":
    st.title("📍 WestProp Project Profiles")
    st.markdown("Explore details of WestProp developments.")

    selected_project = st.selectbox(
        "Select a Project",
        list(project_profiles_info.keys())
    )

    if selected_project:
        project_info = project_profiles_info[selected_project]
        st.subheader(selected_project)
        if project_info.get("image"):
            st.image(project_info["image"], caption=selected_project, use_column_width=True)
        st.write(project_info.get("description", "No description available."))
        if project_info.get("url"):
            st.markdown(f"[Learn More]({project_info['url']})")

        # Display properties associated with this project from properties_df
        st.markdown("#### Available Units in this Project")
        project_units = properties_df[properties_df["project"] == selected_project]
        if not project_units.empty:
            st.dataframe(project_units[["property_type", "price", "bedrooms", "status", "amenities"]])
        else:
            st.info("No specific units listed for this project yet.")




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

    st.markdown("--- ")
    st.info("**Disclaimer:** This calculator provides estimates only. Actual loan terms and payments may vary. Consult with a financial institution for precise figures.")




elif page == "🧬 Investor Match":
    st.title("🧬 Investor Match")
    st.markdown("Find properties that match your investment criteria.")

    st.subheader("Your Investment Preferences")
    min_roi_pref = st.slider("Minimum Desired ROI (%)", 0.0, 20.0, 8.0, step=0.5)
    max_price_pref = st.number_input("Maximum Property Price (USD)", min_value=50000, value=500000, step=10000)
    preferred_property_type = st.multiselect("Preferred Property Type(s)", real_estate_df["property_type"].unique())
    preferred_suburb = st.multiselect("Preferred Suburb(s)", real_estate_df["location_suburb"].unique())
    
    st.subheader("Smart Feature Preferences")
    wants_solar = st.checkbox("Prefers Solar")
    wants_water_recycling = st.checkbox("Prefers Water Recycling")
    wants_smart_locks = st.checkbox("Prefers Smart Locks")
    wants_smart_thermostats = st.checkbox("Prefers Smart Thermostats")
    wants_integrated_security = st.checkbox("Prefers Integrated Security")
    wants_ev_charging = st.checkbox("Prefers EV Charging")

    # Filter properties based on preferences
    matched_properties = real_estate_df.copy()

    matched_properties = matched_properties[
        (matched_properties["ROI_percentage"] >= min_roi_pref) &
        (matched_properties["sale_price_usd"] <= max_price_pref)
    ]

    if preferred_property_type:
        matched_properties = matched_properties[
            matched_properties["property_type"].isin(preferred_property_type)
        ]
    if preferred_suburb:
        matched_properties = matched_properties[
            matched_properties["location_suburb"].isin(preferred_suburb)
        ]

    # Filter by smart feature preferences
    if wants_solar:
        matched_properties = matched_properties[matched_properties["has_solar"] == 1]
    if wants_water_recycling:
        matched_properties = matched_properties[matched_properties["has_water_recycling"] == 1]
    if wants_smart_locks:
        matched_properties = matched_properties[matched_properties["has_smart_locks"] == 1]
    if wants_smart_thermostats:
        matched_properties = matched_properties[matched_properties["has_smart_thermostats"] == 1]
    if wants_integrated_security:
        matched_properties = matched_properties[matched_properties["has_integrated_security"] == 1]
    if wants_ev_charging:
        matched_properties = matched_properties[matched_properties["has_ev_charging"] == 1]

    st.subheader(f"Found {len(matched_properties)} Matching Properties")
    if not matched_properties.empty:
        st.dataframe(matched_properties[[
            "property_id", "location_suburb", "property_type", "sale_price_usd",
            "rental_income_usd_monthly (est)", "ROI_percentage", "has_solar",
            "has_water_recycling", "has_smart_locks", "has_smart_thermostats",
            "has_integrated_security", "has_ev_charging"
        ]])
    else:
        st.info("No properties found matching your criteria. Try adjusting your preferences.")




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
    base_cost_per_sqm = 800 # USD per sqm for basic shell
    total_cost = unit_size_sqm * base_cost_per_sqm

    # Adjust for bedrooms/bathrooms (simplified)
    total_cost += (num_bedrooms - 1) * 5000 # Each additional bedroom adds cost
    total_cost += (num_bathrooms - 1) * 3000 # Each additional bathroom adds cost

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
    st.title("❓ Help & FAQ")
    st.markdown("Find answers to common questions about using the Smart Real Estate ROI Simulator.")

    st.subheader("How to Use the Simulator")
    st.write("1. **Input Property Details:** On the 'Simulator' page, enter the market price, expected monthly rent, and select the smart features the property has or will have.")
    st.write("2. **View ROI Results:** The dashboard will instantly calculate and display the Traditional ROI, Smart ROI (with smart feature savings), and a Predicted ROI from our machine learning model.")
    st.write("3. **Sensitivity Analysis:** Use the sliders in the 'ROI Sensitivity Analysis' section to see how changes in rent, price, or smart feature adoption percentages impact the ROI.")
    st.write("4. **Auto-Fill from Projects:** Select a WestProp project from the dropdown to auto-fill the simulator with its details.")

    st.subheader("Understanding ROI Metrics")
    st.write("**Traditional ROI (Net):** Calculated based on annual rental income minus estimated annual expenses (property tax, maintenance, insurance, agent fees), divided by the market price.")
    st.write("**Smart ROI (Net):** Similar to Traditional ROI, but includes the estimated annual savings from smart features, increasing the net income.")
    st.write("**Predicted ROI (Model):** An ROI forecast generated by our machine learning model, considering various property attributes and smart features.")

    st.subheader("Data & Assumptions")
    st.write("The simulator uses a dataset of real estate properties in Harare, Zimbabwe. All ROI calculations are estimates and are based on the provided input parameters and predefined expense rates.")
    st.write("Smart feature savings are based on general market research and may vary based on actual usage and local conditions.")

    st.subheader("Troubleshooting")
    st.write("**No ROI displayed:** Ensure 'Market Price' is greater than 0 and 'Expected Monthly Rent' is entered.")
    st.write("**Model Prediction Error:** This might occur if input values are outside the range the model was trained on. Try adjusting inputs within reasonable bounds.")
    st.write("**Data Not Loading:** Ensure `real_estate_data_template.csv`, `roi_prediction_model.pkl`, `roi_transformer.pkl`, `model_features.pkl`, and `smart_feature_value_table.csv` are in the correct directories.")

    st.markdown("--- ")
    st.write("For further assistance, please contact WestProp support.")




elif page == "ℹ️ About":
    st.title("ℹ️ About the Smart Real Estate ROI Simulator")
    st.markdown("""
    This interactive dashboard is designed to provide potential investors and homeowners with insights into the Return on Investment (ROI) of real estate properties, with a special focus on the impact of smart home features.

    **Developed by:** WestProp Holdings

    **Purpose:**
    *   To simulate property ROI based on various financial inputs.
    *   To highlight the value proposition of integrating smart and sustainable features into properties.
    *   To provide data-driven insights into the Harare real estate market.
    *   To assist in validating pricing strategies and investor returns for WestProp developments.

    **Key Features:**
    *   **ROI Simulation:** Calculate Traditional, Smart, and AI-Predicted ROI.
    *   **Sensitivity Analysis:** Understand how changes in key variables affect ROI.
    *   **Smart Feature Impact:** Quantify the financial benefits of solar, water recycling, smart locks, and more.
    *   **Property Browser:** Explore a comprehensive dataset of properties with calculated ROIs.
    *   **Interactive Map:** Visualize property ROIs geographically.
    *   **Investment Models:** Learn about different real estate investment strategies.
    *   **Payment Plan Calculator:** Estimate monthly mortgage payments.

    **Data Source:** The data used in this simulator is based on a curated dataset of real estate properties in Harare, Zimbabwe, combined with market research and predictive modeling.

    **Disclaimer:** All simulations and predictions are estimates and should not be considered financial advice. Users are encouraged to consult with financial professionals for personalized investment guidance.
    """)

elif page == "🔔 Alerts":
    st.title("🔔 Alerts & Notifications")
    st.markdown("Stay updated with important market changes, new listings, and personalized alerts.")

    st.info("**No new alerts at this time.** Check back later for updates!")

    st.subheader("Subscribe to Alerts")
    with st.form("alert_subscription_form"):
        alert_email = st.text_input("Enter your email to subscribe to personalized alerts:")
        alert_frequency = st.selectbox("Alert Frequency", ["Daily", "Weekly", "Monthly"])
        alert_submit = st.form_submit_button("Subscribe")

        if alert_submit:
            if alert_email:
                st.success(f"Successfully subscribed {alert_email} to {alert_frequency} alerts!")
                # In a real application, you would save this to a database
            else:
                st.warning("Please enter a valid email address.")

elif page == "🏆 Community Insights":
    st.title("🏆 Community Insights")
    st.markdown("Gain insights from the collective wisdom of the investor community.")

    st.subheader("Investment Sentiment (from ROI Map Voting)")
    try:
        vote_df = pd.read_csv("vote_results.csv")
        if not vote_df.empty:
            # Aggregate votes by property ID
            property_votes = vote_df.groupby("Property ID")["Vote"].value_counts().unstack(fill_value=0)
            property_votes["Total Votes"] = property_votes["Yes"] + property_votes["No"]
            property_votes["Yes % "] = (property_votes["Yes"] / property_votes["Total Votes"]) * 100
            property_votes = property_votes.sort_values(by="Total Votes", ascending=False)

            st.dataframe(property_votes[["Yes", "No", "Total Votes", "Yes % "]].head(10))

            st.info("**Interpretation:** Properties with a higher \"Yes %\" indicate stronger investor interest.")

            # Basic overall sentiment
            total_yes = vote_df[vote_df["Vote"] == "Yes"].shape[0]
            total_no = vote_df[vote_df["Vote"] == "No"].shape[0]
            overall_sentiment = "Positive" if total_yes > total_no else "Negative" if total_no > total_yes else "Neutral"
            st.write(f"**Overall Community Sentiment:** {overall_sentiment} (Yes: {total_yes}, No: {total_no})")

        else:
            st.info("No community votes recorded yet. Participate in the ROI Map to contribute!")
    except FileNotFoundError:
        st.info("No community votes recorded yet. Participate in the ROI Map to contribute!")

    st.markdown("--- ")
    st.info("**Note:** Community insights are based on anonymous user votes and reflect general sentiment, not financial advice.")

elif page == "📉 Market Trends & Analytics":
    st.title("📉 Market Trends & Analytics")
    st.markdown("Analyze historical market data and forecast future trends.")

    st.subheader("Harare Property Price Trends (Conceptual)")
    st.write("This section would typically display interactive charts showing historical property price movements, rental yield trends, and supply/demand dynamics.")
    st.write("**Example Data Points:**")
    st.write("- Average Property Price over time")
    st.write("- Average Rental Yield over time")
    st.write("- Number of Listings vs. Sales Volume")

    # Placeholder for a simple trend chart
    # In a real application, this would be populated with actual time-series data
    trend_data = pd.DataFrame({
        "Year": [2020, 2021, 2022, 2023, 2024],
        "Avg Price (USD)": [100000, 110000, 130000, 150000, 165000],
        "Avg Rental Yield (%)": [7.0, 6.8, 7.2, 7.5, 7.3]
    })
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Avg Price (USD)', color=color)
    ax1.plot(trend_data['Year'], trend_data['Avg Price (USD)'], color=color, marker='o')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Avg Rental Yield (%)', color=color)  # we already handled the x-label with ax1
    ax2.plot(trend_data['Year'], trend_data['Avg Rental Yield (%)'], color=color, marker='x')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    st.pyplot(fig)

    st.markdown("--- ")
    st.info("**Note:** This section provides conceptual examples. Real-time market data integration would require access to dynamic data APIs.")

elif page == "🛡️ Admin Analytics":
    st.title("🛡️ Admin Analytics")
    st.markdown("Admin-only access to detailed usage statistics and system insights.")

    # Password protection for admin page
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == "westprop2025": # Replace with a secure method in production
                st.session_state.admin_logged_in = True
                st.success("Logged in as Admin!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")
    else:
        st.success("Welcome, Admin!")
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

        if st.button("Logout Admin"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()


