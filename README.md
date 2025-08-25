# WestProp Real Estate Dashboard

A comprehensive real estate investment analysis and management platform with ROI simulation, property visualization, and investor engagement tools.

![WestProp Logo](https://via.placeholder.com/200x50.png?text=WestProp+Dashboard)

## 🌟 Features

### 🏠 Smart ROI Simulator
- Calculate potential ROI for properties with and without smart features
- Visualize financial impact of smart home technologies
- Generate detailed PDF reports with investment analysis

### 🗺️ Interactive ROI Map
- Geospatial visualization of property investments
- Filter properties by ROI percentage
- Share custom map views via email

### 🏆 Community Insights
- Track most simulated properties
- View investor leaderboard
- Analyze community voting trends

### 📊 Investment Models
- Compare different investment strategies (Buy-to-Let, Rent-to-Own, etc.)
- Evaluate REIT opportunities
- Calculate payment plans

### 🔧 Shell Unit Customizer
- Design and price custom shell units
- Visualize different customization options
- Get instant cost estimates

### 🔔 Alerts & Notifications
- Email subscription management
- Admin dashboard for managing subscribers
- Bulk email capabilities

## 🔐 Admin Access

### Default Admin Credentials
- **Password**: `westprop2025`

This password is used for all admin-level access across the application, including:
- Admin dashboard
- Voting system administration
- Subscriber management
- System configuration

**Note**: For production use, it's highly recommended to change the default password in the application configuration.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Streamlit
- Required Python packages (see `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd PROJECT-WESTVAULT-2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   SENDER_EMAIL=your-email@gmail.com
   APP_PASSWORD=your-app-specific-password
   ```

### Running the Application

```bash
streamlit run real_estate_dashboard.py
```

## 📂 Project Structure

```
PROJECT-WESTVAULT-2/
├── data/                    # Data files (CSVs, etc.)
├── images/                  # Static images
├── logs/                    # Application logs
├── models/                  # Machine learning models
├── scripts/                 # Utility scripts
├── .env                    # Environment variables
├── email_service.py         # Email functionality
├── hash_gen.py             # Password hashing utilities
├── real_estate_dashboard.py # Main application
└── send_alerts.py          # Alert management system
```

## 🔧 Configuration

### Email Setup
1. Enable 2FA on your Gmail account
2. Generate an App Password
3. Update the `.env` file with your credentials

### Data Storage
- Voting data is stored in `vote_results.csv`
- Subscriber data is managed in `email_alert_subscribers.csv`
- Session logs are stored in `session_log.csv`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For support or inquiries, please contact [support@westprop.com](mailto:support@westprop.com)

---

<div align="center">
  Made with ❤️ by WestProp Team
</div>
