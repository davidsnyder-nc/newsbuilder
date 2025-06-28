#!/bin/bash

# RSS Reader - Package Creator
# Creates a complete deployment package with all files

set -e

PACKAGE_NAME="rss-reader-deployment"
PACKAGE_DIR="./$PACKAGE_NAME"

echo "📦 Creating RSS Reader deployment package..."

# Create package directory
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy application files
echo "📋 Copying application files..."
cp app.py "$PACKAGE_DIR/"
cp ai_summarizer.py "$PACKAGE_DIR/"
cp article_scraper.py "$PACKAGE_DIR/"
cp audio_processor.py "$PACKAGE_DIR/"
cp bookmark_manager.py "$PACKAGE_DIR/"
cp database.py "$PACKAGE_DIR/"
cp rss_manager.py "$PACKAGE_DIR/"

# Copy installation and deployment files
cp install.sh "$PACKAGE_DIR/"
cp deploy.sh "$PACKAGE_DIR/"
cp README.md "$PACKAGE_DIR/"
cp QUICKSTART.md "$PACKAGE_DIR/"

# Create combined installation script
cat > "$PACKAGE_DIR/quick-install.sh" << 'EOF'
#!/bin/bash

# RSS Reader - One-Command Installation
# This script installs everything automatically

set -e

echo "🚀 RSS Reader - Automatic Installation Starting..."

# Run the full installation
chmod +x install.sh
./install.sh

# Deploy application files
chmod +x deploy.sh
./deploy.sh

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Set up your Gemini API key:"
echo "   cd ~/rss-reader"
echo "   cp .env.example .env"
echo "   nano .env  # Add your GEMINI_API_KEY"
echo ""
echo "2. Get your API key from: https://aistudio.google.com/"
echo ""
echo "3. Start the application:"
echo "   ./start.sh"
echo ""
echo "4. Open browser to: http://localhost:5000"
echo ""
echo "🎉 Your RSS Reader is ready to use!"
EOF

chmod +x "$PACKAGE_DIR/quick-install.sh"

# Create archive
echo "📦 Creating deployment archive..."
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_DIR"

echo "✅ Package created successfully!"
echo ""
echo "📁 Files included:"
ls -la "$PACKAGE_DIR"
echo ""
echo "📦 Archive: ${PACKAGE_NAME}.tar.gz"
echo ""
echo "🚀 To deploy on your Debian server:"
echo "1. Copy ${PACKAGE_NAME}.tar.gz to your server"
echo "2. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "3. Install: cd $PACKAGE_NAME && ./quick-install.sh"
echo "4. Configure API key and start: cd ~/rss-reader && ./start.sh"