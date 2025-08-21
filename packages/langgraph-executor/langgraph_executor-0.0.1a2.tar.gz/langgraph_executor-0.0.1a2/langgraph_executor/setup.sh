#!/bin/bash

echo "Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python -m pip install -r requirements.txt

# Deactivate environment 
deactivate

# Generate protobuf files
# echo "Generating Python protobuf files..."
# source .venv/bin/activate
# ./generate_proto.sh

echo "Python setup complete!"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"