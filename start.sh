#!/bin/bash

# RSS Reader Startup Script
# Starts the Streamlit application with proper configuration

set -e

# Default port
PORT=5000
VENV_DIR="venv"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --port PORT    Port number (default: 5000)"
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

echo "🚀 Starting RSS Reader..."
echo "📱 Application will be available at: http://localhost:$PORT"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found: $VENV_DIR"
    echo "Please run the install.sh script first."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Ensure .streamlit directory exists
mkdir -p .streamlit

# Create or update Streamlit config
cat > .streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = $PORT

[theme]
primaryColor = "#1976d2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f5f5f5"
textColor = "#000000"
EOF

# Start the application
echo "🔄 Starting Streamlit server on port $PORT..."
exec streamlit run app.py --server.port "$PORT" --server.address "0.0.0.0"