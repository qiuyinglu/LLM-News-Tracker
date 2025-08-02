#!/bin/bash

# Shell script to activate the virtual environment (macOS/Linux)
echo "Activating virtual environment..."
source virtualenv/bin/activate

echo ""
echo "✓ Virtual environment activated!"
echo "To run the project: cd src && python main.py"
echo "To deactivate: deactivate"
echo ""

# Start a new shell session with the virtual environment active
exec "$SHELL"
