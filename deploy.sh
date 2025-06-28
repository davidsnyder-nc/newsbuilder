#!/bin/bash

# RSS Reader Deployment Script
# Copies all application files to the installation directory

set -e

# Default installation directory
INSTALL_DIR="$HOME/rss-reader"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --dir DIR      Installation directory (default: ~/rss-reader)"
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

echo "📦 Deploying RSS Reader application files..."
echo "Target directory: $INSTALL_DIR"

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Installation directory not found: $INSTALL_DIR"
    echo "Please run the install.sh script first."
    exit 1
fi

# Copy application files
echo "📋 Copying application files..."
cp app.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: app.py not found in current directory"
cp ai_summarizer.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: ai_summarizer.py not found"
cp article_scraper.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: article_scraper.py not found"
cp audio_processor.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: audio_processor.py not found"
cp bookmark_manager.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: bookmark_manager.py not found"
cp database.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: database.py not found"
cp rss_manager.py "$INSTALL_DIR/app/" 2>/dev/null || echo "Warning: rss_manager.py not found"

# Copy documentation
cp README.md "$INSTALL_DIR/" 2>/dev/null || echo "Warning: README.md not found"
cp QUICKSTART.md "$INSTALL_DIR/" 2>/dev/null || echo "Warning: QUICKSTART.md not found"

# Create requirements.txt for reference
cat > "$INSTALL_DIR/requirements.txt" << 'EOF'
streamlit==1.39.0
feedparser==6.0.11
google-genai==0.8.3
google-cloud-texttospeech==2.17.2
pydub==0.25.1
requests==2.32.3
trafilatura==1.12.2
EOF

# Create systemd service file template
cat > "$INSTALL_DIR/rss-reader.service" << 'EOF'
[Unit]
Description=RSS Reader with AI Summarization
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/rss-reader
Environment=PATH=/path/to/rss-reader/venv/bin
ExecStart=/path/to/rss-reader/start.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Deployment completed!"
echo ""
echo "📁 Files copied to: $INSTALL_DIR/app/"
echo "📋 Requirements file: $INSTALL_DIR/requirements.txt"
echo "🔧 Systemd service template: $INSTALL_DIR/rss-reader.service"
echo ""
echo "🚀 To start the application:"
echo "   cd $INSTALL_DIR"
echo "   ./start.sh"