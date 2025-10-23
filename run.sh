#!/bin/bash
# Wrapper script that automatically activates venv and runs the phrase continuation app

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOUR
# Activate virtual environment
source venv/bin/activate

# Check if activation worked
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Failed to activate virtual environment"
    echo "Please run: ./install_dependencies.sh"
    exit 1