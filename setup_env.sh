#!/bin/bash

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
    echo "Virtual environment activation script not found."
    exit
fi

# Install dependencies
pip install -r requirements.txt

# Check if the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is not activated."
    exit
else
    echo "Virtual environment is activated."
fi