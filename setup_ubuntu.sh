#!/bin/bash
echo "=== DOKYOS AUTO INSTALLER ==="

# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip python3-venv -y

# Install TA-LIB dependencies
apt install build-essential -y
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib && ./configure --prefix=/usr && make && make install
cd .. && rm -rf ta-lib*

# Create virtual environment
python3 -m venv dokyos_env
source dokyos_env/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs data/historical learning_memory

# Set permissions
chmod +x deploy_service.sh
chmod +x main.py

echo "=== INSTALLATION COMPLETE ==="
echo "Run: source dokyos_env/bin/activate"
echo "Then: python main.py"
