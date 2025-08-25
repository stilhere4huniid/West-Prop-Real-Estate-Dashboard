#!/bin/bash
set -e  # Exit on error

echo "=== Setting up environment ==="

# Install system dependencies
echo "Installing system dependencies..."
apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    git

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
echo "Creating directories..."
mkdir -p data logs .streamlit
chmod -R 755 .

# Create empty data files if they don't exist
echo "Initializing data files..."
for file in email_alert_subscribers session_log vote_results viewing_requests; do
    if [ ! -f "data/${file}.csv" ]; then
        touch "data/${file}.csv"
        chmod 666 "data/${file}.csv"
    fi
done

echo "=== Setup completed successfully ==="
