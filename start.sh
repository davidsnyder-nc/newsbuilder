#!/bin/bash

# RSS Reader Startup Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default values
DEFAULT_PORT=5000
DEFAULT_HOST="0.0.0.0"

# Parse command line arguments
PORT=$DEFAULT_PORT
HOST=$DEFAULT_HOST

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --port PORT    Port to run the server on (default: 5000)"
            echo "  -h, --host HOST    Host to bind to (default: 0.0.0.0)"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Use environment variables if set, otherwise use command line args
FINAL_PORT=${PORT:-$DEFAULT_PORT}
FINAL_HOST=${HOST:-$DEFAULT_HOST}

echo "Starting RSS Reader..."
echo "Host: $FINAL_HOST"
echo "Port: $FINAL_PORT"
echo ""
echo "Access the application at: http://localhost:$FINAL_PORT"
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment
source venv/bin/activate

# Note: API key can be configured through the web interface Settings page

# Start the Streamlit application
streamlit run app.py --server.port=$FINAL_PORT --server.address=$FINAL_HOST --server.headless=true