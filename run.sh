#!/bin/bash

echo "========================================"
echo "Student Health Monitoring System"
echo "Python + Flask + Machine Learning"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Python found! Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Dependencies installed successfully!"
echo
echo "Starting the application..."
echo
echo "The web interface will open at: http://localhost:5000"
echo "Press Ctrl+C to stop the application"
echo

python3 app.py
