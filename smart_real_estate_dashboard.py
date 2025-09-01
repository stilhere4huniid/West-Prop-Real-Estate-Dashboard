import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
import datetime
import os # Ensure os is imported
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import joblib
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import json
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Load smart feature value proposition table
smart_value_df = pd.read_csv("data/smart_feature_value_table.csv")

# --- CONFIG ---
st.set_page_config(page_title="Smart Real Estate ROI Simulator", layout="centered")
st.image("westprop_logo.png", width=200)

model = joblib.load("models/roi_predictor.pkl")

# --- SESSION STATE DEFAULTS ---
if "market_price" not in st.session_state:
    st.session_state.market_price = 120000
if "monthly_rent" not in st.session_state:
    st.session_state.monthly_rent = 1000
if "has_solar" not in st.session_state:
    st.session_state.has_solar = True
if "has_recycling" not in st.session_state:
    st.session_state.has_recycling = False
if "has_smart_lock" not in st.session_state:
    st.session_state.has_smart_lock = False 
if "selected_session_idx" not in st.session_state:
    st.session_state.selected_session_idx = 0

# --- Property Data Structure (for Filter/Compare Feature) ---
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
# **INSERTION POINT 1: Add this dictionary here**
# Store image paths relative to the script location or use absolute paths
# IMPORTANT: Ensure image files exist in a 'project_images' subfolder
project_profiles_info = {
    "The Hills Lifestyle Estate": {
        "image": "project_images/the_hills_estate.png", # Adjusted path
        "description": "Zimbabwe's first integrated luxury golf estate offering villas and residential stands. Features include golf access, mall access, wellness center, and high security.",
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
        has_solar = st.checkbox(
            "☀️ Has Solar",
            value=st.session_state.has_solar,
            help="Adds rooftop solar panels. Boosts savings and ROI."
        )
        has_recycling = st.checkbox(
            "💧 Has Water Recycling",
            value=st.session_state.has_recycling,
            help="Includes greywater systems for irrigation or reuse."
        )
        has_smart_lock = st.checkbox(
            "🔐 Has Smart Locks",
            value=st.session_state.has_smart_lock,
            help="Improves security with digital locks. Adds value to rentals."
        )
        submit_sim = st.form_submit_button("Update Simulation")

    # Only update session state and save snapshot when form is submitted
    if submit_sim:
        st.session_state.market_price = market_price
        st.session_state.monthly_rent = monthly_rent
        st.session_state.has_solar = has_solar
        st.session_state.has_recycling = has_recycling
        st.session_state.has_smart_lock = has_smart_lock

        # --- Use session state for calculations as before ---
        annual_rent = st.session_state.monthly_rent * 12
        monthly_savings = (
            (40 if st.session_state.has_solar else 0)
            + (15 if st.session_state.has_recycling else 0)
            + (5 if st.session_state.has_smart_lock else 0)
        )
        annual_savings = monthly_savings * 12
        roi = (
            (annual_rent / st.session_state.market_price) * 100
            if st.session_state.market_price > 0 else 0
        )
        smart_roi = (
            ((annual_rent + annual_savings) / st.session_state.market_price) * 100
            if st.session_state.market_price > 0 else 0
        )
        features = pd.DataFrame([{
            "MarketPrice": st.session_state.market_price,
            "MonthlyRent": st.session_state.monthly_rent,
            "HasSolar": int(st.session_state.has_solar),
            "HasRecycling": int(st.session_state.has_recycling),
            "HasSmartLock": int(st.session_state.has_smart_lock),
        }])
        predicted_roi = model.predict(features)[0]

        # --- Save snapshot to server log ---
        snapshot = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Market Price": st.session_state.market_price,
            "Monthly Rent": st.session_state.monthly_rent,
            "Has Solar": st.session_state.has_solar,
            "Has Water Recycling": st.session_state.has_recycling,
            "Has Smart Lock": st.session_state.has_smart_lock,
            "Predicted ROI": round(predicted_roi, 2)
        }
        snapshot_df = pd.DataFrame([snapshot])
        file_path = "session_log.csv"
        snapshot_df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)

    # --- Always use session state for calculations and display ---
    annual_rent = st.session_state.monthly_rent * 12
    monthly_savings = (
        (40 if st.session_state.has_solar else 0)
        + (15 if st.session_state.has_recycling else 0)
        + (5 if st.session_state.has_smart_lock else 0)
    )
    annual_savings = monthly_savings * 12
    roi = (
        (annual_rent / st.session_state.market_price) * 100
        if st.session_state.market_price > 0 else 0
    )
    smart_roi = (
        ((annual_rent + annual_savings) / st.session_state.market_price) * 100
        if st.session_state.market_price > 0 else 0
    )
    features = pd.DataFrame([{
        "MarketPrice": st.session_state.market_price,
        "MonthlyRent": st.session_state.monthly_rent,
        "HasSolar": int(st.session_state.has_solar),
        "HasRecycling": int(st.session_state.has_recycling),
        "HasSmartLock": int(st.session_state.has_smart_lock),
    }])
    predicted_roi = model.predict(features)[0]

    st.subheader("📊 ROI Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Traditional ROI", f"{roi:.2f} %")
    col2.metric("Smart ROI", f"{smart_roi:.2f} %")
    col3.metric("Predicted ROI (Model)", f"{predicted_roi:.2f} %")

    st.markdown("### 💸 Estimated Annual & Lifetime Savings")
    st.write(f"**Annual Savings:** ${annual_savings:,}")
    st.write(f"**5-Year Savings:** ${annual_savings * 5:,}")
    st.write(f"**10-Year Savings:** ${annual_savings * 10:,}")

    roi_df = pd.DataFrame({
        "ROI Type": ["Traditional ROI", "Smart ROI", "Predicted ROI"],
        "Value": [roi, smart_roi, predicted_roi]
    })
    fig, ax = plt.subplots()
    ax.bar(roi_df["ROI Type"], roi_df["Value"], color=["#003366", "#FFC72C", "#4A4A4A"])
    ax.set_ylabel("ROI (%)")
    ax.set_title("ROI Comparison")
    st.pyplot(fig)

    # --- Save the ROI chart to buffer
    roi_chart_buf = io.BytesIO()
    fig.savefig(roi_chart_buf, format="png")
    roi_chart_buf.seek(0)
    st.session_state.roi_chart_buf = roi_chart_buf

    # --- Prepare snapshot data for download ---
    snapshot = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Market Price": st.session_state.market_price,
        "Monthly Rent": st.session_state.monthly_rent,
        "Has Solar": st.session_state.has_solar,
        "Has Water Recycling": st.session_state.has_recycling,
        "Has Smart Lock": st.session_state.has_smart_lock,
        "Predicted ROI": round(predicted_roi, 2)
    }
    # Convert all values to native Python types
    snapshot_clean = {k: (int(v) if isinstance(v, (np.integer,)) else float(v) if isinstance(v, (np.floating,)) else v) for k, v in snapshot.items()}
    snapshot_json = json.dumps(snapshot_clean, indent=2)
    st.download_button(
        label="💾 Download Session Snapshot (JSON)",
        data=snapshot_json,
        file_name="westprop_session_snapshot.json",
        mime="application/json"
    )

    # --- Load Previous Session Feature (ONLY in Simulator tab) ---
    if os.path.exists("session_log.csv"):
        log_df = pd.read_csv("session_log.csv")
        if not log_df.empty:
            log_df = log_df[::-1].reset_index(drop=True)
            # Use synced index from session state, default to 0
            selected_idx = st.session_state.get("selected_session_idx", 0)
            selected_idx = min(selected_idx, len(log_df.index)-1)  # Prevent out-of-range
            selected_idx = st.selectbox(
                "📂 Load a Previous Session",
                options=log_df.index,
                index=selected_idx,
                format_func=lambda i: f"{log_df.loc[i, 'Timestamp']} | ROI: {log_df.loc[i, 'Predicted ROI']}% | Price: ${log_df.loc[i, 'Market Price']}"
            )
            if st.button("Load Selected Session"):
                row = log_df.loc[selected_idx]
                st.session_state.market_price = row["Market Price"]
                st.session_state.monthly_rent = row["Monthly Rent"]
                st.session_state.has_solar = bool(row["Has Solar"])
                st.session_state.has_recycling = bool(row["Has Water Recycling"])
                st.session_state.has_smart_lock = bool(row["Has Smart Lock"])
                st.session_state.selected_session_idx = selected_idx  # Keep in sync
                st.success("✅ Session loaded! Please click 'Update Simulation' to apply these values.")
        else:
            st.info("No simulations found yet. Run a simulation in the Simulator tab to get started.")

            # --- ROI Sensitivity Analysis ---
    st.markdown("### 🌀 ROI Sensitivity Analysis (What-If Scenarios)")
    st.caption("Adjust the sliders to see how changes in key variables affect ROI.")

    # Define ranges for sensitivity
    rent_range = st.slider("Monthly Rent Range (USD)", 0, 5000, (int(st.session_state.monthly_rent * 0.7), int(st.session_state.monthly_rent * 1.3)))
    price_range = st.slider("Market Price Range (USD)", 50000, 2000000, (int(st.session_state.market_price * 0.7), int(st.session_state.market_price * 1.3)))
    solar_adopt = st.slider("Solar Adoption (%)", 0, 100, 100 if st.session_state.has_solar else 0, step=10)
    recycling_adopt = st.slider("Water Recycling Adoption (%)", 0, 100, 100 if st.session_state.has_recycling else 0, step=10)
    lock_adopt = st.slider("Smart Lock Adoption (%)", 0, 100, 100 if st.session_state.has_smart_lock else 0, step=10)

    base_price = st.session_state.market_price
    base_rent = st.session_state.monthly_rent

    # Updated ROI calculation to use adoption percentages
    def calc_roi(price, rent, solar_pct, recycling_pct, lock_pct):
        annual_rent = rent * 12
        # Each feature's savings is scaled by its adoption percentage
        monthly_savings = (
            40 * (solar_pct / 100) +
            15 * (recycling_pct / 100) +
            5 * (lock_pct / 100)
        )
        annual_savings = monthly_savings * 12
        return ((annual_rent + annual_savings) / price) * 100 if price > 0 else 0

    # Add this above your tornado chart code:
    mode = st.radio(
        "Tornado Chart Mode",
        ["Full Impact (0%→100%)", "What-If (Current→100%)"],
        index=0,
        help="Choose whether to see the full possible impact of each feature, or the impact from your current scenario."
    )

    if mode == "Full Impact (0%→100%)":
        sensitivity = {
            "Monthly Rent": [
                calc_roi(base_price, rent_range[0], solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(base_price, rent_range[1], solar_adopt, recycling_adopt, lock_adopt)
            ],
            "Market Price": [
                calc_roi(price_range[0], base_rent, solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(price_range[1], base_rent, solar_adopt, recycling_adopt, lock_adopt)
            ],
            "Solar Adoption": [
                calc_roi(base_price, base_rent, 0, recycling_adopt, lock_adopt),
                calc_roi(base_price, base_rent, 100, recycling_adopt, lock_adopt)
            ],
            "Water Recycling": [
                calc_roi(base_price, base_rent, solar_adopt, 0, lock_adopt),
                calc_roi(base_price, base_rent, solar_adopt, 100, lock_adopt)
            ],
            "Smart Lock": [
                calc_roi(base_price, base_rent, solar_adopt, recycling_adopt, 0),
                calc_roi(base_price, base_rent, solar_adopt, recycling_adopt, 100)
            ]
        }
    else:  # What-If (Current→100%)
        sensitivity = {
            "Monthly Rent": [
                calc_roi(base_price, rent_range[0], solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(base_price, rent_range[1], solar_adopt, recycling_adopt, lock_adopt)
            ],
            "Market Price": [
                calc_roi(price_range[0], base_rent, solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(price_range[1], base_rent, solar_adopt, recycling_adopt, lock_adopt)
            ],
            "Solar Adoption": [
                calc_roi(base_price, base_rent, solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(base_price, base_rent, 100, recycling_adopt, lock_adopt)
            ],
            "Water Recycling": [
                calc_roi(base_price, base_rent, solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(base_price, base_rent, solar_adopt, 100, lock_adopt)
            ],
            "Smart Lock": [
                calc_roi(base_price, base_rent, solar_adopt, recycling_adopt, lock_adopt),
                calc_roi(base_price, base_rent, solar_adopt, recycling_adopt, 100)
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
        }
        st.session_state.market_price = selected_row["price"]
        st.session_state.monthly_rent = default_rents.get(selected_row["property_type"], 1000)
        # Example: set features based on amenities
        st.session_state.has_solar = "Solar" in (selected_row["amenities"] or [])
        st.session_state.has_recycling = "Water Recycling" in (selected_row["amenities"] or [])
        st.session_state.has_smart_lock = "Lock-up Shell" in (selected_row["amenities"] or [])
        st.info(f"Auto-filled values for {selected_project_option}. You can adjust them below.")

# --- My Simulations ---
elif page == "🗂️ My Simulations":
    st.title("🗂️ My Simulations History")

    if os.path.exists("session_log.csv"):
        log_df = pd.read_csv("session_log.csv")
        if not log_df.empty:
            log_df = log_df[::-1].reset_index(drop=True)
            st.dataframe(log_df, use_container_width=True)

            selected_idx = st.selectbox(
                "Select a session to load",
                options=log_df.index,
                format_func=lambda i: f"{log_df.loc[i, 'Timestamp']} | ROI: {log_df.loc[i, 'Predicted ROI']}% | Price: ${log_df.loc[i, 'Market Price']}"
            )
            if st.button("Load Selected Simulation"):
                row = log_df.loc[selected_idx]
                st.session_state.market_price = row["Market Price"]
                st.session_state.monthly_rent = row["Monthly Rent"]
                st.session_state.has_solar = bool(row["Has Solar"])
                st.session_state.has_recycling = bool(row["Has Water Recycling"])
                st.session_state.has_smart_lock = bool(row["Has Smart Lock"])
                st.session_state.selected_session_idx = selected_idx  # <-- This line syncs the dropdown
                st.success("✅ Simulation loaded! Go to the Simulator tab to view and work with these values.")
        else:
            st.info("No simulations found yet. Run a simulation in the Simulator tab to get started.")
    else:
        st.info("No simulations found yet. Run a simulation in the Simulator tab to get started.")

# --- Alerts Tab ---
elif page == "🔔 Alerts":
    st.title("🔔 Subscribe for Email Alerts")
    st.markdown("""
    Stay up to date with the latest WestProp projects, price changes, and investment opportunities.
    Enter your email below to receive important updates directly to your inbox.
    """)

    alert_email = st.text_input("Your Email Address")
    if st.button("Subscribe for Alerts"):
        if alert_email and "@" in alert_email:
            alerts_file = "email_alert_subscribers.csv"
            import csv
            from datetime import datetime
            with open(alerts_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([alert_email, datetime.now().isoformat()])
            st.success("✅ You have been subscribed for email alerts!")
        else:
            st.warning("Please enter a valid email address.")

# --- EXECUTIVE SUMMARY ---
elif page == "📈 Executive Summary":
    st.title("💼 Key Takeaways:")
    st.markdown("""
    - Smart homes deliver **+0.8% ROI gain** on average
    - Smart homes deliver **~$429 in annual savings** from solar, water recycling, and smart locks
    - Projected **10-year smart savings** gain: ~$4,296 per unit
    - **AI-predicted ROI** offers additional validation for investor targeting
    - Based on Zimbabwe market trends and smart infrastructure adoption           
    - Ideal for scaling sustainable, profitable developments like **WestProp's Millennium Heights, Pomona City, The Hills Lifestyle Estate, Pokugara Residential Estate**
    """)

    # Pull from session state
    market_price = st.session_state.market_price
    monthly_rent = st.session_state.monthly_rent
    has_solar = st.session_state.has_solar
    has_recycling = st.session_state.has_recycling
    has_smart_lock = st.session_state.has_smart_lock

    # Recalculate
    annual_rent = monthly_rent * 12
    monthly_savings = (40 if has_solar else 0) + (15 if has_recycling else 0) + (5 if has_smart_lock else 0)
    annual_savings = monthly_savings * 12
    roi = (annual_rent / market_price) * 100 if market_price > 0 else 0
    smart_roi = ((annual_rent + annual_savings) / market_price) * 100 if market_price > 0 else 0
    features = pd.DataFrame([{
        "MarketPrice": market_price,
        "MonthlyRent": monthly_rent,
        "HasSolar": int(has_solar),
        "HasRecycling": int(has_recycling),
        "HasSmartLock": int(has_smart_lock)
    }])
    predicted_roi = model.predict(features)[0]

    # --- Visual Recap ---
    st.subheader("📊 Visual Recap")
    st.caption("This chart compares estimated ROI under different scenarios based on your inputs.")
    recap_df = pd.DataFrame({
        "ROI Type": ["Traditional ROI", "Smart ROI", "Predicted ROI"],
        "Value": [roi, smart_roi, predicted_roi]
    })

    fig, ax = plt.subplots()
    ax.bar(recap_df["ROI Type"], recap_df["Value"], color=["#003366", "#FFC72C", "#4A4A4A"])
    ax.set_ylabel("ROI (%)")
    ax.set_title("Simulated ROI Gain with Smart Features")
    st.pyplot(fig)

    # --- Save the ROI chart to buffer for PDF ---
    import io
    roi_chart_buf = io.BytesIO()
    fig.savefig(roi_chart_buf, format="png")
    roi_chart_buf.seek(0)
    st.session_state.roi_chart_buf = roi_chart_buf

    # --- Real Use Case ---
    st.subheader("🧭 Real Use Case: WestProp Strategy")
    st.markdown("""
If WestProp integrates these smart features across developments like:

- 🏢 **Millennium Heights**
- 🌳 **Pomona City**
- 🏠 **The Hills Lifestyle Estate**
- 🏘️ **Pokugara Residential Estate**

...they can offer:

- More attractive ROI packages to investors
- Tangible long-term savings to buyers
- A competitive edge as a *tech-forward sustainable developer*

**This dashboard helps validate pricing, investor returns, and green value.**
""")
  

    # --- Dynamic PDF Generation ---
    def generate_pdf(market_price, monthly_rent, has_solar, has_recycling, has_smart_lock, roi, smart_roi, predicted_roi, annual_savings, roi_chart_buf):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        try:
            c.drawImage("westprop_logo.png", 40, 750, width=120, preserveAspectRatio=True, mask='auto')
        except:
            pass

        text = c.beginText(40, 720)
        text.setFont("Helvetica-Bold", 14)
        text.textLine("WestProp Smart ROI Summary (Live Estimate)")
        text.setFont("Helvetica", 11)
        text.textLine("")
        text.textLine("This one-pager simulates property ROI based on selected inputs,")
        text.textLine("aligned with WestProp's smart & sustainable vision.")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Inputs:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Market Price: ${market_price:,}")
        text.textLine(f"- Monthly Rent: ${monthly_rent:,}")
        text.textLine(f"- Has Solar: {'Yes' if has_solar else 'No'}")
        text.textLine(f"- Has Water Recycling: {'Yes' if has_recycling else 'No'}")
        text.textLine(f"- Has Smart Locks: {'Yes' if has_smart_lock else 'No'}")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("ROI Results:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Traditional ROI: {roi:.2f}%")
        text.textLine(f"- Smart ROI: {smart_roi:.2f}%")
        text.textLine(f"- Predicted ROI (Model): {predicted_roi:.2f}%")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Estimated Savings:")
        text.setFont("Helvetica", 11)
        text.textLine(f"- Annual: ${annual_savings:,}")
        text.textLine(f"- 5-Year: ${annual_savings * 5:,}")
        text.textLine(f"- 10-Year: ${annual_savings * 10:,}")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("Interpretation:")
        text.setFont("Helvetica", 11)
        text.textLine("This smart-enhanced unit yields a higher projected ROI based on added upgrades.")
        text.textLine("Cost savings are driven by solar, water efficiency, and access control features.")
        text.textLine("")

        text.setFont("Helvetica-Bold", 12)
        text.textLine("WestProp Use Case:")
        text.setFont("Helvetica", 11)
        text.textLine("Ideal for validating pricing strategy in developments such as:")
        text.textLine("• Millennium Heights")
        text.textLine("• Pomona City")
        text.textLine("• The Hills Lifestyle Estate")
        text.textLine("• Pokugara Residential Estate")
        text.textLine("")

        text.setFont("Helvetica-Oblique", 10)
        text.textLine("*This is an auto-generated summary using real-time inputs. All values are estimates.*")
        
        c.drawText(text)

        # --- Draw the ROI chart image ---
        try:
            c.drawImage(roi_chart_buf, 60, 200, width=400, height=220, mask='auto')
        except Exception as e:
            print("Error drawing chart image:", e)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_data = generate_pdf(
        market_price,
        monthly_rent,
        has_solar,
        has_recycling,
        has_smart_lock,
        roi,
        smart_roi,
        predicted_roi,
        annual_savings,
        st.session_state.roi_chart_buf
)


    st.download_button(
        label="📄 Download Full One-Pager PDF",
        data=pdf_data,
        file_name="WestProp_Smart_ROI_Summary.pdf",
        mime="application/pdf"
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

# --- MAP VIEW ---
elif page == "🗺️ ROI Map":
    st.title("🗺️ Interactive ROI Map with Heatmap View")

    st.sidebar.markdown("---")
    min_roi = st.sidebar.slider("Minimum ROI to display (%)", 0.0, 20.0, 9.0, step=0.1)
    show_heatmap = st.sidebar.checkbox("Show Heatmap Layer", value=True)
    show_markers = st.sidebar.checkbox("Show ROI Markers", value=True)

    # Load data safely
    try:
        df = pd.read_csv("westprop_streamlit_dataset.csv")
    except FileNotFoundError:
        st.error("Error: westprop_streamlit_dataset.csv not found. Please ensure the file exists.")
        st.stop() # Stop execution if data is missing

    # Define the match_project_name function inside the ROI Map tab
    def match_project_name(lat_clicked, lon_clicked, dataset, threshold=0.0005):
        for _, row in dataset.iterrows():
            if abs(row["Latitude"] - lat_clicked) <= threshold and abs(row["Longitude"] - lon_clicked) <= threshold:
                return row["Project"]
        return "Unknown Location"

    filtered_df = df[df["ROI (%)"] >= min_roi]

    m = folium.Map(location=[-17.8, 31.02], zoom_start=12)

    if show_markers:
        for _, row in filtered_df.iterrows():
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=f"{row['Project']} — ROI: {row['ROI (%)']}%",
                tooltip=row["Project"]
            ).add_to(m)

    if show_heatmap:
        heat_data = [[row["Latitude"], row["Longitude"], row["ROI (%)"]] for _, row in filtered_df.iterrows()]
        HeatMap(heat_data, radius=25).add_to(m)

    # Move the map_data and related code inside the ROI Map tab with proper indentation
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

    # === MAP CLICK EVENT + VOTING SECTION ===
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        # Match to project name
        matched_project = match_project_name(lat, lon, df)

        # Find the ROI at the clicked location, or use a default if not found
        roi_match = df[(abs(df["Latitude"] - lat) < 0.0005) & (abs(df["Longitude"] - lon) < 0.0005)]
        if not roi_match.empty and "ROI (%)" in roi_match.columns:
            simulated_roi = roi_match.iloc[0]["ROI (%)"]
        else:
            simulated_roi = 0.0  # Default value if not found

        st.markdown(f"📍 **You clicked:** `{lat:.5f}, {lon:.5f}`")
        st.markdown(f"🏢 **Project Detected:** `{matched_project}`")
        st.markdown(f"💡 **Simulated ROI at this location:** `{simulated_roi:.2f}%`")

        st.subheader("🗳️ Would You Invest in This Location?")
        vote = st.radio("Your Vote", ["Yes", "No"], horizontal=True, help="Would you consider investing in a property at this location?")

        if st.button("Submit Vote"):
            vote_record = pd.DataFrame([{
                "Project": matched_project,
                "Latitude": lat,
                "Longitude": lon,
                "ROI (%)": round(simulated_roi, 2),
                "Vote": vote,
                "Timestamp":datetime.now().isoformat()
            }])

            try:
                existing_votes = pd.read_csv("vote_results.csv")
                vote_data = pd.concat([existing_votes, vote_record], ignore_index=True)
            except FileNotFoundError:
                vote_data = vote_record

            vote_data.to_csv("vote_results.csv", index=False)
            st.success("✅ Your vote has been recorded for this project!")
    
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
        # Keep only one admin preview section
        try:
            recent_votes = pd.read_csv("vote_results.csv")
            st.dataframe(recent_votes.tail(10))      
        except:
            st.warning("No votes recorded yet.")

          # 👇 Reset Button    
        if st.button("🧹 Reset All Votes"):
            with open("vote_results.csv", "w") as f:
             f.write("Project,Latitude,Longitude,ROI (%),Vote,Timestamp\n")
             st.success("🗳️ All votes cleared. Voting restarted fresh.")        
     
    if st.button("🔓 Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.go_to_roi_map = True
        st.info("Logged out.")
        st.rerun()

    # === Optional Vote Summary Chart ===
    if st.session_state.get("admin_logged_in", False):
        st.subheader("📊 Vote Summary by Project")
    
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
        except pd.errors.EmptyDataError:            st.info("Voting file is empty. No votes have been recorded yet.")   
        except Exception as e:
            st.error(f"An error occurred while generating the chart: {e}")

# --- PROJECT PROFILES PAGE ---
# **INSERTION POINT 2: Replace the existing elif block with this one**
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

# --- 💸PAYMENT PLAN CALCULATOR PAGE ---
elif page == "💸 Payment Plan Calculator":
    st.title("💸 Payment Plan Calculator")
    project_choice = st.selectbox("Select Project for Payment Plan", ["Pokugara Townhouses", "The Hills Lifestyle Estate"])

    if project_choice == "Pokugara Townhouses":
        st.subheader("Pokugara Townhouse Payment Plan")
        st.markdown("_(Based on: 30% Deposit, $1k Commitment, 3-6mo Interest-Free Balance)_ ")
        pok_price = st.number_input("Property Price (USD)", 357000, 409000, 357000, step=1000, key="pok_price", help="Total price of the townhouse.") # Use specific range
        pok_deposit_perc = 30
        pok_commit_fee = 1000
        pok_months = st.radio("Balance Payment Term (Interest-Free)", [3, 6], horizontal=True, key="pok_months", help="Interest-free months available to pay the balance.")

        pok_deposit_amt = pok_price * (pok_deposit_perc / 100)
        pok_balance = pok_price - pok_deposit_amt - pok_commit_fee
        pok_monthly_payment = pok_balance / pok_months if pok_months > 0 else 0

        st.metric("Commitment Fee", f"${pok_commit_fee:,}")
        st.metric(f"Deposit Amount ({pok_deposit_perc}%)", f"${pok_deposit_amt:,.2f}")
        st.metric(f"Monthly Payment (for {pok_months} months)", f"${pok_monthly_payment:,.2f}")
        st.metric("Total Price", f"${pok_price:,}")

    elif project_choice == "The Hills Lifestyle Estate":
        st.subheader("The Hills Lifestyle Estate Payment Plan")
        st.markdown("_(Based on: 30% Deposit, $10k Commitment, 24mo Balance - Interest from Mo 6)_ ")
        hills_price = st.number_input("Property Price / Stand Price (USD)", 70000, 1600000, 380000, step=1000, key="hills_price",  help="Price of the villa or stand in The Hills Estate.") # Wider range
        hills_deposit_perc = 30
        hills_commit_fee = 10000
        hills_total_months = 24
        hills_interest_free_months = 6
        # Assuming an illustrative interest rate after 6 months, e.g., 10% p.a. on remaining balance
        hills_interest_rate_pa = st.slider("Interest Rate (% p.a. after month 6)", 0.0, 15.0, 10.0, step=0.5, key="hills_interest",help="Annual interest rate for months 7–24 on the balance.")

        hills_deposit_amt = hills_price * (hills_deposit_perc / 100)
        hills_initial_balance = hills_price - hills_deposit_amt - hills_commit_fee

        # Simplified calculation: Assume equal payments for first 6 months, then recalculate with interest
        # A more accurate calculation would involve amortization, but this gives an idea.
        hills_payment_part1 = hills_initial_balance / hills_total_months # Rough equal split
        hills_balance_after_6mo = hills_initial_balance - (hills_payment_part1 * hills_interest_free_months)

        # Calculate approximate payment for remaining 18 months with interest
        # Using a simple interest approximation for illustration
        remaining_months = hills_total_months - hills_interest_free_months
        monthly_interest_rate = (hills_interest_rate_pa / 100) / 12
        # Approximation: Average balance * interest + principal portion
        if remaining_months > 0:
             # Using annuity formula factor for approximation: P = L[c(1 + c)^n]/[(1 + c)^n - 1]
             if monthly_interest_rate > 0:
                 factor = (monthly_interest_rate * (1 + monthly_interest_rate)**remaining_months) / ((1 + monthly_interest_rate)**remaining_months - 1)
                 hills_payment_part2 = hills_balance_after_6mo * factor
             else:
                 hills_payment_part2 = hills_balance_after_6mo / remaining_months # If 0% interest
        else:
            hills_payment_part2 = 0

        st.metric("Commitment Fee", f"${hills_commit_fee:,}")
        st.metric(f"Deposit Amount ({hills_deposit_perc}%)", f"${hills_deposit_amt:,.2f}")
        st.metric(f"Est. Monthly Payment (Months 1-6)", f"${hills_payment_part1:,.2f}")
        st.metric(f"Est. Monthly Payment (Months 7-24, with {hills_interest_rate_pa}% interest)", f"${hills_payment_part2:,.2f}")
        st.metric("Total Price (excluding interest)", f"${hills_price:,}")
        st.caption("Interest calculation is approximate. Consult WestProp for exact figures.")

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

                # Add link at the bottom of the column
                url_val = properties_to_compare.loc[index, 'url']
                if url_val and isinstance(url_val, str) and url_val.startswith('http'):
                    st.markdown(f"[Link]({url_val})", unsafe_allow_html=True)
                else:
                    st.caption("Link: Not Available")

# --- 🧬 Investor Match ---  
    elif len(compare_list) == 1:
        st.info("Select at least one more property to compare.")
    else:
        st.info("Select properties using the checkboxes above to compare them side-by-side.")

elif page == "🧬 Investor Match":
    st.title("🧬 Match Me with a Property")

    profile = st.selectbox("Select Your Investor Profile", [
        "Diaspora Investor",
        "Local First-Time Buyer",
        "Family Upsizing",
        "Retiree",
        "Passive Income Seeker"
    ])

    if profile == "Diaspora Investor":
        st.subheader("🌍 Diaspora Investor Match")
        st.markdown("""
        **🔹 Ideal Projects:** Radisson Aparthotel, Pomona Flats, Millennium Heights  
        **🔹 Rationale:** Low-maintenance units, REIT access, strong rental income  
        **🔹 Suggested Budget:** $5,000 – $150,000  
        **🔹 ROI Focus:** Income over appreciation  
        """)

    elif profile == "Local First-Time Buyer":
        st.subheader("🏡 First-Time Buyer Match")
        st.markdown("""
        **🔹 Ideal Projects:** Pomona Flats (1- or 2-bed), Millennium Heights Studio  
        **🔹 Rationale:** Affordable units with installment options  
        **🔹 Suggested Budget:** $50,000 – $130,000  
        **🔹 ROI Focus:** Long-term ownership and equity building  
        """)

    elif profile == "Family Upsizing":
        st.subheader("👨‍👩‍👧‍👦 Family Home Match")
        st.markdown("""
        **🔹 Ideal Projects:** Pokugara Townhouses, The Hills Townhouses  
        **🔹 Rationale:** Spacious units, secure gated estates, schools nearby  
        **🔹 Suggested Budget:** $300,000 – $600,000  
        **🔹 ROI Focus:** Lifestyle + capital preservation  
        """)

    elif profile == "Retiree":
        st.subheader("🌿 Retirement Buyer Match")
        st.markdown("""
        **🔹 Ideal Projects:** The Hills Retirement Cluster, Garden Units  
        **🔹 Rationale:** Peaceful environments, easy access, low stairs, security  
        **🔹 Suggested Budget:** $100,000 – $350,000  
        **🔹 ROI Focus:** Lifestyle, not yield  
        """)

    elif profile == "Passive Income Seeker":
        st.subheader("💸 Passive Investor Match")
        st.markdown("""
        **🔹 Ideal Projects:** Radisson REIT, Millennium Heights Airbnb Units  
        **🔹 Rationale:** High rental demand, serviced models, professional management  
        **🔹 Suggested Budget:** $5,000 – $300,000  
        **🔹 ROI Focus:** Yield, dividends, low effort  
        """)

# --- 🔧 Shell Unit Customizer ---
elif page == "🔧 Shell Unit Customizer":
    st.title("🔧 Millennium Heights Block 4 – Shell Unit Finishing Estimator")

    import pandas as pd
    df = pd.read_csv("data/shell_unit_customization_data.csv")

    unit_type = st.selectbox("Choose Unit Type", df["Unit Type"],  help="Choose the layout of the apartment shell you’re customizing.")
    finish_option = st.radio("Choose Finishing Package", ["Standard", "Premium", "Custom"], help="Pick a finish option or enter your own budget for custom." )

    row = df[df["Unit Type"] == unit_type].iloc[0]

    # --- Clean and convert shell price ---
    shell_price_str = str(row["Shell Price (USD)"]).replace("$", "").replace(",", "")
    try:
        shell_price = float(shell_price_str)
    except ValueError:
        st.error(f"Could not convert shell price ", {row["Shell Price (USD)"]}, " to a number.")
        shell_price = 0.0 # Default to 0 if conversion fails

    # --- Determine and clean/convert finish cost ---
    if finish_option == "Standard":
        finish_cost_str = str(row["Standard Finish Cost (USD)"]).replace("$", "").replace(",", "")
        try:
            finish_cost = float(finish_cost_str)
        except ValueError:
            st.error(f"Could not convert standard finish cost '{row['Standard Finish Cost (USD)']}' to a number.")
            finish_cost = 0.0
    elif finish_option == "Premium":
        finish_cost_str = str(row["Premium Finish Cost (USD)"]).replace("$", "").replace(",", "")
        try:
            finish_cost = float(finish_cost_str)
        except ValueError:
            st.error(f"Could not convert premium finish cost '{row['Premium Finish Cost (USD)']}' to a number.")
            finish_cost = 0.0
    else: # Custom input
        finish_cost = st.number_input("Enter Custom Finish Cost (USD)", min_value=0.0, value=0.0, step=1000.0)

    # --- Calculate total estimate ---
    total_estimate = shell_price + finish_cost

    # --- Display results with formatting ---
    st.markdown(f"**🏗️ Shell Price:** ${shell_price:,.2f}")
    st.markdown(f"**🎨 Finish Cost ({finish_option}):** ${finish_cost:,.2f}")
    st.markdown(f"**Total Estimate:** ${total_estimate:,.2f}")

elif page == "♻️ Smart Feature Value Proposition":
     st.title("♻️ Smart Feature Value Proposition")
     st.markdown("""
    This section highlights how selected smart features—already available in your ROI simulator—
    enhance long-term property value, reliability, and sustainability in Zimbabwe.
    """)

     st.dataframe(smart_value_df, use_container_width=True)

     st.caption("🔎 Figures are based on Zimbabwe’s energy/water context, property market trends, and smart home ROI studies.")

# --- HELP PAGE ---
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
    2. Enter your property’s market price and expected rent
    3. Toggle smart features (solar, recycling, smart locks)
    4. See dynamic ROI results, savings, and predictions

    ---

    ## 📈 ROI Metrics Explained

    - **Traditional ROI:** Rent-based ROI with no smart features  
    - **Smart ROI:** Includes cost savings from selected smart upgrades  
    - **Predicted ROI (Model):** AI-predicted estimate trained on real patterns

    ---

    ## 🗺️ ROI Map Tips

    - Use the **ROI Map** to explore project locations and ROI heat levels
    - Click any location to simulate potential ROI at that point
    - After clicking, you can cast a **“Would You Invest?” vote** to help us understand investor sentiment

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

    - Compare **Direct Purchase** vs **Radisson REIT**
    - Simulate returns, risk, and income
    - Designed for both retail investors and institutional buyers

    ---

    ## 💸 Payment Plan Calculator

    - Pokugara and Hills-specific calculators
    - See deposit, commitment fees, monthly payment timelines
    - Includes interest simulation for Hills' 24-month plan

    ---

    ## 🔍 Property Browser

    - Advanced filters by project, type, price, status, amenities
    - Compare properties side-by-side
    - Based on real WestProp listing data

    ---

    ## 🧬 Investor Match

    - Pick your profile (Diaspora Investor, Retiree, First-Time Buyer, etc.)
    - Get auto-matched to best-fit projects + rationale
    - Uses curated logic from WestProp’s research & buyer personas

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
    Log in as admin via the ROI Map tab. The Admin Analytics tab will then appear in the sidebar.

    > _Note: These features are restricted to authorized staff for data privacy and business security._

    ---
                
     ### ℹ️ About Tab
    - Learn about the dashboard’s purpose and structure

    - Read about WestProp’s mission, CEO Ken Sharpe, and values
    - Get context for how each tool supports investor insights and smart growth  

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
        - **Full Impact (0%→100%)**: See the maximum possible ROI impact for each variable.
        - **What-If (Current→100%)**: See the ROI impact of increasing each variable from its current value to 100%.
    - The tornado chart and table below it will update to show which factors have the biggest effect on your returns.

    ## 🗂️ My Simulations
    - Instantly review and reload your past simulation sessions.     

    ---                  

    ## 💡 Tooltips

    Hover over any sidebar element, slider, or checkbox to get quick explanations.

    ---

    ## 📬 Need Support?

    For questions, feedback, or collaboration inquiries, please email [tutu@westprop.com](mailto:tutu@westprop.com)

    ---
    """)

    st.info("This platform was built to align with WestProp\'s tech-forward real estate vision. Thank you for exploring it!")
    # Add help content

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
    - **Streamlit**, **scikit-learn**, **folium**, **Reportlab**, and **WestProp project data**
    
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

# --- Community Insights ---
elif page == "🏆 Community Insights":
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

# --- MARKET TRENDS & ANALYTICS PAGE ---
elif page == "📉 Market Trends & Analytics":
    st.title("📉 Zimbabwe Market Trends & Analytics (2024)")
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
    smart_years = [2019, 2020, 2021, 2022, 2023, 2024]
    adoption = [5, 8, 12, 18, 25, 33]
    st.line_chart(pd.DataFrame({"Year": smart_years, "Smart Feature Adoption (%)": adoption}).set_index("Year"))

    # --- Smart Feature Adoption Trends (Zimbabwe Urban New Builds, Estimated) ---
    st.subheader("🔌 Smart Feature Adoption Trends")
    st.caption("Estimated % of new builds with solar, water recycling, and smart locks in Zimbabwe (2019–2024). Sources: World Bank, GreenCape, Coldwell Banker, local developer interviews.")

    years = [2019, 2020, 2021, 2022, 2023, 2024]
    solar = [5, 8, 12, 18, 25, 33]
    water = [2, 3, 4, 6, 8, 10]
    locks = [2, 3, 5, 7, 8, 10]
    adoption_df = pd.DataFrame({
        "Solar (%)": solar,
        "Water Recycling (%)": water,
        "Smart Locks (%)": locks
    }, index=years)
    st.line_chart(adoption_df)

# --- ADMIN ANALYTICS PAGE ---
elif page == "🛡️ Admin Analytics":
    if not st.session_state.get("admin_logged_in", False):
        st.warning("Admin access required. Please log in as admin in the ROI Map tab.")
        st.stop()
    st.title("🛡️ Admin Analytics Dashboard")

    # --- Feature Selection Panel ---
    st.markdown("#### 🛠️ Choose Analytics to Display")
    features_to_show = st.multiselect(
        "Select analytics features to display:",
        [
            "Simulation Activity",
            "Most Popular Simulated Market Price",
            "Sentiment Heatmap (Voting)",
            "Download Raw Data"
        ],
        default=[
            "Simulation Activity",
            "Most Popular Simulated Market Price",
            "Sentiment Heatmap (Voting)",
            "Download Raw Data"
        ]
    )

    # --- User Activity (Simulations) ---
    if "Simulation Activity" in features_to_show:
        st.subheader("📊 Simulation Activity")
        if os.path.exists("session_log.csv"):
            sim_df = pd.read_csv("session_log.csv")
            if not sim_df.empty:
                st.metric("Total Simulations", len(sim_df))
                sim_df["Date"] = pd.to_datetime(sim_df["Timestamp"], errors="coerce").dt.date
                sim_counts = sim_df.groupby("Date").size()
                st.line_chart(sim_counts)
            else:
                st.info("No simulation data yet.")
        else:
            st.info("No simulation data yet.")

    # --- Most Popular Simulated Market Price ---
    if "Most Popular Simulated Market Price" in features_to_show:
        st.subheader("🏆 Most Popular Simulated Market Price")
        if os.path.exists("session_log.csv"):
            sim_df = pd.read_csv("session_log.csv")
            if not sim_df.empty and "Market Price" in sim_df.columns:
                most_sim_price = sim_df["Market Price"].mode()[0]
                st.metric("Most Simulated Market Price", f"${most_sim_price:,.0f}")
            else:
                st.info("No simulation data yet.")
        else:
            st.info("No simulation data yet.")

    # --- Sentiment Heatmap (Voting) ---
    if "Sentiment Heatmap (Voting)" in features_to_show:
        st.subheader("🗺️ Sentiment Heatmap (Voting Data)")
        if os.path.exists("vote_results.csv"):
            vote_df = pd.read_csv("vote_results.csv")
            if not vote_df.empty:
                import folium
                from streamlit_folium import st_folium
                from folium.plugins import HeatMap

                m = folium.Map(location=[-17.8, 31.02], zoom_start=12)
                # Yes votes = green, No votes = red
                for _, row in vote_df.iterrows():
                    color = "#4CAF50" if row["Vote"] == "Yes" else "#F44336"
                    folium.CircleMarker(
                        location=[row["Latitude"], row["Longitude"]],
                        radius=8,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.6,
                        popup=f"{row['Project']} ({row['Vote']})"
                    ).add_to(m)
                # Add heatmap for Yes votes
                yes_heat = vote_df[vote_df["Vote"] == "Yes"]
                if not yes_heat.empty:
                    HeatMap(yes_heat[["Latitude", "Longitude"]].values, radius=25).add_to(m)
                st_folium(m, width=700, height=500)
            else:
                st.info("No voting data yet.")
        else:
            st.info("No voting data yet.")

    # --- Download Buttons for Admin ---
    if "Download Raw Data" in features_to_show:
        st.subheader("⬇️ Download Raw Data")
        if os.path.exists("session_log.csv"):
            with open("session_log.csv", "rb") as f:
                st.download_button("Download Simulation Log (CSV)", f, file_name="session_log.csv")
        if os.path.exists("vote_results.csv"):
            with open("vote_results.csv", "rb") as f:
                st.download_button("Download Voting Data (CSV)", f, file_name="vote_results.csv")
