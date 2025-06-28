#!/bin/bash

# RSS Reader Local Installation Script
# Works without system package management

set -e

echo "🚀 Setting up RSS Reader locally..."

# Use current directory as project directory
PROJECT_DIR="$(pwd)"
echo "📁 Using current directory: $PROJECT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

PYTHON_CMD="python3"
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🏠 Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install streamlit==1.39.0
pip install feedparser==6.0.11
pip install google-genai==0.8.3
pip install google-cloud-texttospeech==2.17.2
pip install pydub==0.25.1
pip install requests==2.32.3
pip install trafilatura==1.12.2

# Create data and logs directories
echo "📋 Creating data structure..."
mkdir -p data
mkdir -p logs

# Create/update startup script
cat > start.sh << 'EOF'
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
EOF

chmod +x start.sh

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping RSS Reader..."

# Find and kill any running streamlit processes for this app
pkill -f "streamlit run app.py" || echo "No running RSS Reader processes found"

echo "RSS Reader stopped."
EOF

chmod +x stop.sh

echo "✅ Local installation completed successfully!"
echo ""
echo "📋 Your RSS Reader is ready to use:"
echo "1. Your application files are already in place"
echo "2. Virtual environment created with all dependencies"
echo "3. Configure your Gemini API key through the web interface:"
echo "   - Go to Settings page"
echo "   - Expand 'Configure API Keys'"
echo "   - Enter your API key and save"
echo ""
echo "🚀 To start the application:"
echo "   ./start.sh                    # Start on default port 5000"
echo "   ./start.sh --port 8080        # Start on custom port"
echo "   ./start.sh --host 127.0.0.1   # Start on localhost only"
echo ""
echo "🛑 To stop the application:"
echo "   ./stop.sh"
echo ""
echo "📁 Project location: $PROJECT_DIR"