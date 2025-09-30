#!/bin/bash
echo "Installing sgit on Ubuntu..."

# Update package list
sudo apt update

# Install Python and pip if not present
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo apt install -y python3 python3-pip python3-venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv sgit-env

# Activate virtual environment
echo "Activating virtual environment..."
source sgit-env/bin/activate

# Install sgit in development mode
echo "Installing sgit..."
pip install -e .

echo "Installation complete!"
echo ""
echo "To use sgit:"
echo "1. Activate the virtual environment: source sgit-env/bin/activate"
echo "2. Run: sgit --help"
echo ""
echo "Or use directly: python3 run_sgit.py --help"