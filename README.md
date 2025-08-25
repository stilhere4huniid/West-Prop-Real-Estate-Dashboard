<div align="center">
  <!-- Replace the URL below with your actual logo URL -->
  <img src="https://via.placeholder.com/300x100?text=WestProp+Logo" alt="WestProp Logo" width="300"/>
  
  # Real Estate Investment Analysis Dashboard
</div>

> **Note**: To display your logo, replace the image URL above with your actual logo URL. The current image is a placeholder.

> **Disclaimer**: This is an independent project built for educational and portfolio demonstration purposes. This dashboard is not an official product of WestProp Holdings Limited. All WestProp brand assets, trademarks, and references are used respectfully and remain the exclusive property of WestProp Holdings Limited.

## 🚀 Project Overview

A comprehensive real estate investment analysis and management platform with ROI simulation, property visualization, and investor engagement tools. This project serves as a demonstration of modern web development, data visualization, and real estate financial modeling capabilities.

## 📝 Important Notice

- This application is a conceptual prototype and should not be used for making actual investment decisions
- All property data and calculations are for demonstration purposes only
- The project is not affiliated with, endorsed by, or connected to WestProp Holdings Limited
- Any resemblance to actual products or services is coincidental

## 🏢 About WestProp Holdings

[WestProp Holdings](https://westprop.com/) is a leading real estate development company in Zimbabwe, known for its innovative and sustainable property developments. This project is a tribute to their forward-thinking approach to real estate development and investment.

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

## 🔐 Security & Access Control

### Admin Access
- **No default credentials** - All admin access is secured with individual credentials
- Multi-factor authentication (MFA) is required for all admin accounts
- Session management with automatic timeout

### Security Best Practices
1. **Environment Variables**
   - Store sensitive information in `.env` files (never commit these to version control)
   - Use strong, unique passwords for all services
   - Rotate credentials regularly

2. **Data Protection**
   - All sensitive data is encrypted at rest and in transit
   - Regular security audits and updates
   - Principle of least privilege for all system access

3. **Secure Development**
   - Dependency scanning for known vulnerabilities
   - Regular security updates
   - Secure coding practices enforced

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

For support or inquiries, please contact [stillhere4huniid@gmail.com](mailto:stillhere4huniid@gmail.com)

---

<div align="center">
  Made with ❤️ by WestProp Team
</div>
