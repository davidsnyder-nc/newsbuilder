#!/bin/bash

# RSS Reader with AI Summarization - Installation Script
# For Debian/Ubuntu systems

set -e  # Exit on any error

echo "🚀 Installing RSS Reader with AI Summarization..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install Python 3.11 and pip if not already installed
echo "🐍 Installing Python 3.11 and dependencies..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y git curl wget build-essential

# Use current directory as project directory
PROJECT_DIR="$(pwd)"
echo "📁 Using current directory as project directory: $PROJECT_DIR..."

# Create virtual environment
echo "🏠 Creating Python virtual environment..."
python3.11 -m venv venv
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

# Note: .env.example file should be copied from the repository
# Users will copy .env.example to .env and add their API key

# Create startup script
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

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY not set!"
    echo "   Please set your Gemini API key in the .env file or as an environment variable."
    echo "   The app will still run but AI features won't work."
    echo ""
fi

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

echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Your application files are already in place"
echo "2. Configure your Gemini API key through the web interface:"
echo "   - Go to Settings page"
echo "   - Expand 'Configure API Keys'"
echo "   - Enter your API key and save"
echo ""
echo "🚀 To start the application:"
echo "   cd $PROJECT_DIR"
echo "   ./start.sh                    # Start on default port 5000"
echo "   ./start.sh --port 8080        # Start on custom port"
echo "   ./start.sh --host 127.0.0.1   # Start on localhost only"
echo ""
echo "🛑 To stop the application:"
echo "   ./stop.sh"
echo ""
echo "📁 Project location: $PROJECT_DIR"