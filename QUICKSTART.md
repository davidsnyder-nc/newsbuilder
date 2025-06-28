# Quick Start Guide - RSS Reader

## One-Command Installation

```bash
# Download and run installation
curl -fsSL https://raw.githubusercontent.com/your-repo/rss-reader/main/quick-install.sh | bash
```

## Manual Installation (3 Steps)

### 1. Install Dependencies
```bash
./install.sh
```

### 2. Start Application
```bash
./start.sh                    # Default: http://localhost:5000
./start.sh --port 8080        # Custom port: http://localhost:8080
```

### 3. Configure API Key in Web Interface

1. Open browser to `http://localhost:5000`
2. Go to "Settings" page
3. Expand "Configure API Keys" 
4. Enter your Gemini API key from [Google AI Studio](https://aistudio.google.com/)
5. Click "Save API Key"

## Common Commands

```bash
# Start the app
./start.sh

# Start on different port
./start.sh --port 8080

# Stop the app
./stop.sh

# View logs
tail -f logs/app.log
```

## First Use

1. Open browser to `http://localhost:5000`
2. Go to "RSS Feeds" tab
3. Add your first feed (e.g., https://feeds.bbci.co.uk/news/rss.xml)
4. Browse articles on the main page
5. Bookmark articles and generate AI summaries

## Troubleshooting

- **Port busy**: Use `./start.sh --port 8080`
- **Permission denied**: Run `chmod +x *.sh`
- **No API key**: Configure in Settings page via web interface

That's it! Your RSS reader is ready to use.