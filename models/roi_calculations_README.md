# ROI Simulator – Smart Real Estate Intelligence Dashboard

This notebook provides comprehensive analysis of how smart home features impact property Return on Investment (ROI) in the Harare real estate market. It uses real-world property data to quantify the financial benefits of various smart home technologies.

## 📊 Key Features

### 1. ROI Calculations
- **Gross ROI (Traditional ROI)**: Basic ROI based on annual rental income relative to property price
- **Smart ROI**: Enhanced ROI calculation incorporating savings from smart home features
- **Net ROI**: ROI after accounting for property expenses (taxes, maintenance, insurance, agent fees)

### 2. Smart Feature Analysis
Quantifies the financial impact of various smart home features:
- ☀️ Solar Panels - Reduces electricity costs and provides energy independence
- 💧 Water Recycling - Greywater systems for irrigation and reuse
- 🔐 Smart Locks - Enhanced security and convenience features
- 🌡️ Smart Thermostats - Optimizes heating and cooling efficiency
- 🏠 Integrated Security - Comprehensive property protection system
- ⚡ EV Charging - Electric vehicle charging infrastructure

### 3. Financial Metrics
- Monthly and annual savings from each smart feature
- 5-year and 10-year lifetime savings projections
- Comparative analysis of properties with vs. without smart features

### 4. Visualizations
- ROI comparison charts
- Savings breakdown by feature type
- Property performance metrics

## 📈 How It Works

1. **Data Input**: Loads property data including:
   - Property details (size, location, type)
   - Smart feature indicators
   - Rental income estimates
   - Expense data (taxes, maintenance, etc.)

2. **Calculations**:
   - Computes traditional ROI based on rental income
   - Adds value from smart feature savings
   - Adjusts for various property expenses
   - Projects long-term financial benefits

3. **Output**:
   - Detailed ROI metrics for each property
   - Comparative analysis reports
   - Visual representations of financial benefits

## 🛠️ Usage

1. Ensure all required Python packages are installed (pandas, matplotlib, seaborn, numpy)
2. Update the input data file path if necessary
3. Run the notebook cells sequentially
4. Review the generated reports and visualizations

## 📋 Requirements
- Python 3.7+
- pandas
- matplotlib
- seaborn
- numpy

## 📊 Sample Outputs
- ROI comparison charts
- Savings breakdown by feature
- Property performance metrics
- Long-term financial projections

## 📂 Data Sources

### Property Dataset (`real_estate_data_template.csv`)
- **Source**: [Property.co.zw](https://www.property.co.zw) - Zimbabwe's leading real estate listings platform
- **Collection Method**: Manually collected from Property.co.zw listings in Harare
- **Time Period**: Data reflects market conditions as of August 2025
- **Records**: 300+ properties
- **Property Types**:
  - Townhouses
  - Flats/Apartments
  - Luxury Homes
- **Key Attributes**:
  - Location (suburb/neighborhood)
  - Property size (stand and building area)
  - Bedrooms and bathrooms
  - Sale price (USD)
  - Estimated monthly rental income
  - Smart feature indicators
  - Annual expenses (tax, maintenance, insurance, agent fees)
  - Calculated ROI metrics

### Smart Feature Savings
- **Basis**:
  - Local utility rates in Harare
  - Average usage patterns for residential properties
  - Industry benchmarks for smart home technologies
  - Maintenance and operational cost estimates

## ⚠️ Limitations
- Savings estimates are based on average usage patterns
- Actual savings may vary based on:
  - Local climate conditions
  - Individual usage habits
  - Maintenance and installation costs
  - Changes in utility rates
- The model assumes proper installation and maintenance of all smart features
- Results should be used as one of several factors in investment decisions

## 📝 Notes
- The analysis uses estimated savings values for smart features
- Regular data updates are recommended for most accurate results
- For the most current ROI calculations, use the interactive Streamlit dashboard
