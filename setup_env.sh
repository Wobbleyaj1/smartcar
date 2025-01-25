#!/bin/sh

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "Python could not be found. Please install Python."
    exit
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate the virtual environment
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt