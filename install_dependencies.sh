#!/bin/bash
# Comprehensive M1 Mac setup script for phrase continuation application

set -e  # Exit on any error


# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"



# Verify activation
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated: $VIRTUAL_ENV"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with MPS support for M1
echo "Installing PyTorch with M1 MPS support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install transformers and other dependencies
echo "Installing transformers and dependencies..."
pip install transformers>=4.30.0
pip install tokenizers>=0.13.0
pip install accelerate>=0.20.0


# Verify installations
echo "Verifying installations..."
python3 -c "
import sys
print(f'Python: {sys.version}')

    import torch
    print(f'PyT
try:
    import psutil
    print(f'psutil: {psutil.__version__}')
except ImportError:
    print('psutil not available (memory monitoring disabled)')

try:
    import flask
    print(f'Flask: {flask.__version__}')
except ImportError:
    print('Flask not available (web interface disabled)')

print('All core dependencies installed successfully!')
"

# Test the application
echo "Testing the application..."
echo "Testing Markov fallback...