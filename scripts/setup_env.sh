#!/bin/bash
# Environment setup script

echo "GLS Warehouse Safety - Setup Script"
echo "===================================="

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate
echo "Activating environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p data/dataset/images/{train,val,test}
mkdir -p data/dataset/labels/{train,val,test}
mkdir -p outputs/{logs,reports,videos}

echo "Setup complete!"
echo "Run: source venv/bin/activate"
