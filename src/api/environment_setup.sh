#!/bin/bash

# Ensure Python 3.11 is installed
if ! command -v python3.11 &> /dev/null
then
    echo "Python 3.11 not found. Please install it before running this script."
    exit 1
fi

# Create a virtual environment
pyenv local 3.11.0
python3.11 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "✅ Environment setup complete. Run 'source venv/bin/activate' to activate."
