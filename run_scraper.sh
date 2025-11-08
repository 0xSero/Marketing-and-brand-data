#!/bin/bash
# Quick start script for Marketing Knowledge Database Scraper

echo "=================================="
echo "Marketing Knowledge Database Scraper"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Starting scraper..."
echo ""

# Run the scraper
python main.py --all

echo ""
echo "Scraping complete! Check the logs directory for details."
echo "Run 'python main.py --stats' to view statistics."
