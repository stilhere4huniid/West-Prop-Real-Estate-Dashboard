#!/bin/bash
# Install system dependencies
apt-get update
apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data logs .streamlit

# Create empty data files if they don't exist
touch data/email_alert_subscribers.csv
touch data/session_log.csv
touch data/vote_results.csv
touch data/viewing_requests.csv

# Set proper permissions
chmod -R 755 .
