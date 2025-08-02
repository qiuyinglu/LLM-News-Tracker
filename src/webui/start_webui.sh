#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LLM News Thread Web UI...${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project root directory (two levels up from webui)
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT" || {
    echo "Error: Could not change to project root directory"
    exit 1
}

# Check if virtual environment exists
if [ ! -f "virtualenv/bin/python" ]; then
    echo "Error: Virtual environment not found at virtualenv/bin/python"
    echo "Please ensure the virtual environment is set up correctly."
    exit 1
fi

# Check if the web UI app exists
if [ ! -f "src/webui/run.py" ]; then
    echo "Error: Web UI application not found at src/webui/run.py"
    exit 1
fi

# Start the web UI
echo -e "${GREEN}Starting Flask development server...${NC}"
echo -e "Access the web interface at: ${YELLOW}http://localhost:5000${NC}"
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop the server"
echo ""

# Run the web UI with the virtual environment Python
./virtualenv/bin/python src/webui/run.py

echo ""
echo -e "${YELLOW}Web UI server stopped.${NC}"
