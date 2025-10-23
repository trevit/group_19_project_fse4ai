#!/bin/bash
# Comprehensive M1 Mac setup script for phrase continuation application

set -e  # Exit on any error

echo "Setting up M1-optimized phrase continuation app..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Warning: This script is optimized for macOS (M1 Mac)"
fi

# Remove existing venv if it exists and has issues
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

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
pip install psutil>=5.9.0
pip install numpy>=1.24.0
pip install flask>=2.3.0

# Verify installations
echo "Verifying installations..."
python3 -c "
import sys
print(f'Python: {sys.version}')

try:
    import torch
    print(f'PyTorch: {torch.__version__}')
    print(f'MPS available: {torch.backends.mps.is_available()}')
    print(f'MPS built: {torch.backends.mps.is_built()}')
except ImportError as e:
    print(f'PyTorch import failed: {e}')
    sys.exit(1)

try:
    import transformers
    print(f'Transformers: {transformers.__version__}')
except ImportError as e:
    print(f'Transformers import failed: {e}')
    sys.exit(1)

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
echo "Testing Markov fallback..."
python3 continue_phrase.py "The future of technology" --use-markov

echo ""
echo "Testing transformer functionality..."
python3 continue_phrase.py "Machine learning is" --verbose || echo "Transformers test failed, but Markov fallback works"

echo ""
echo "Setup complete!"
echo ""
echo "Usage examples:"
echo "# Activate environment (run this in each new terminal):"
echo "source venv/bin/activate"
echo ""
echo "# Basic usage:"
echo "python3 continue_phrase.py \"Your phrase here\""
echo ""
echo "# With performance monitoring:"
echo "python3 continue_phrase.py \"Your phrase here\" --verbose"
echo ""
echo "# Force Markov model (always works):"
echo "python3 continue_phrase.py \"Your phrase here\" --use-markov"
echo ""
echo "# Start web interface:"
echo "./start_web_app.sh"