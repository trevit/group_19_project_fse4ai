#!/bin/bash
# Start web application and open Safari

echo "Starting web application for phrase generation..."

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Function to open Safari after server starts
open_safari() {
    sleep 3  # Wait for server to start

    open -a Safari http://localhost:5001
}

# Start the background process to open Safari
open_safari &

echo "Starting web server at http://localhost:5001"
echo "Safari will open automatically in a few seconds..."

echo ""
