#!/bin/bash
# Setup script for Job Market Demand Forecaster

set -e

echo "🚀 Setting up Job Market Demand Forecaster..."

# Check Python version
echo "Checking Python version..."
python --version || { echo "Python not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend
echo "Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Start backend: uvicorn backend.app.main:app --reload"
echo "  3. Start frontend: cd frontend && npm run dev"
echo ""
echo "To train a model:"
echo "  python ml/train.py --csv data/processed/software_engineer_new_york,ny.csv --role 'Software Engineer' --location 'New York, NY'"
