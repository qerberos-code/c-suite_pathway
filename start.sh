#!/bin/bash

# C-Suite Pathway Program Startup Script

echo "Starting C-Suite Pathway Program Website..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting Flask application..."
echo "Website will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
