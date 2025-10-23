#!/bin/bash
# Wrapper script that automatically activates venv and runs the phrase continuation app

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run: ./install_dependencies.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if activation worked
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Failed to activate virtual environment"
    echo "Please run: ./install_dependencies.sh"
    exit 1
fi

# Run the application with all passed arguments
python3 continue_phrase.py "$@"