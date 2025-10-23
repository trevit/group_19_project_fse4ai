#!/bin/bash
# Start web application and open Safari

echo "Starting web application for phrase generation..."

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    echo "Error: web_app.py not found. Make sure you're in the project99 directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Function to open Safari after server starts
open_safari() {
    sleep 3  # Wait for server to start
    echo "Opening Safari..."
    open -a Safari http://localhost:5001
}

# Start the background process to open Safari
open_safari &

# Start the Flask application
echo "Starting web server at http://localhost:5001"
echo "Safari will open automatically in a few seconds..."
echo "Press Ctrl+C to stop"
echo ""

python3 web_app.py