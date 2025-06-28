# RSS Reader - Debian Server Deployment Instructions

## Overview

I've created a complete deployment package for running your RSS Reader on your local Debian server. The package includes automatic dependency installation, database setup, and startup scripts with customizable port configuration.

## What's Included

✅ **Automatic Installation Script** (`install.sh`)
- Installs Python 3.11 and all required system dependencies
- Creates virtual environment with all Python packages
- Sets up project structure automatically
- No user intervention required

✅ **Application Files**
- Complete RSS Reader application with all modules
- Clean Material Design interface (no icons/decorative images)
- Uses only Gemini and Google services (no OpenAI dependencies)
- Automatic SQLite database creation in `data/` directory

✅ **Startup & Management Scripts**
- `start.sh` - Start the application with customizable port/host
- `stop.sh` - Stop the application gracefully
- Environment variable support via `.env` file

✅ **Documentation**
- Complete README.md with troubleshooting
- Quick start guide
- Installation and usage instructions

## Deployment Package

I've created `rss-reader-deployment.tar.gz` containing everything you need.

## Installation on Your Debian Server

### Option 1: One-Command Installation

```bash
# Download and extract the package
tar -xzf rss-reader-deployment.tar.gz
cd rss-reader-deployment

# Run automatic installation (installs everything)
./quick-install.sh

# Set up your API key
cd ~/rss-reader
cp .env.template .env
nano .env  # Add: GEMINI_API_KEY=your_key_here

# Start the application
./start.sh
```

### Option 2: Step-by-Step Installation

```bash
# Extract package
tar -xzf rss-reader-deployment.tar.gz
cd rss-reader-deployment

# Install dependencies and set up environment
./install.sh

# Deploy application files
./deploy.sh

# Configure API key
cd ~/rss-reader
cp .env.template .env
nano .env  # Add your GEMINI_API_KEY

# Start application
./start.sh
```

## Starting the Application

```bash
cd ~/rss-reader

# Default: Start on port 5000, bind to all interfaces
./start.sh

# Custom port
./start.sh --port 8080

# Bind to localhost only
./start.sh --host 127.0.0.1

# Custom port and host
./start.sh --port 8080 --host 192.168.1.100
```

## Accessing the Application

Once started, the RSS Reader will be available at:
- **Local access**: `http://localhost:5000`
- **Network access**: `http://your-server-ip:5000`
- **Custom port**: `http://your-server-ip:your-port`

## Database Setup

The database is **automatically created** when the application first runs:
- Location: `~/rss-reader/data/rss_reader.db`
- Type: SQLite (no server required)
- Tables: Created automatically for feeds, articles, bookmarks, and settings

## API Key Setup

You need a Google Gemini API key for AI features:

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add it to your `.env` file:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Project Structure

After installation, your server will have:

```
~/rss-reader/
├── app/                    # Application files
│   ├── app.py             # Main Streamlit application
│   ├── ai_summarizer.py   # AI summarization
│   ├── article_scraper.py # Web scraping
│   ├── audio_processor.py # Text-to-speech
│   ├── bookmark_manager.py# Bookmarks
│   ├── database.py        # Database operations
│   └── rss_manager.py     # RSS management
├── data/                  # Auto-created database directory
│   └── rss_reader.db     # SQLite database (auto-created)
├── venv/                  # Python virtual environment
├── .env                   # Your API key configuration
├── start.sh              # Start script
├── stop.sh               # Stop script
├── README.md             # Full documentation
└── QUICKSTART.md         # Quick reference
```

## Key Features

1. **No User Intervention Required**: Database and dependencies install automatically
2. **Customizable Port**: Use any port with `--port` flag
3. **Network Binding**: Control access with `--host` flag  
4. **Clean Interface**: Material Design without icons or decorative images
5. **AI-Powered**: Gemini-based summarization and text-to-speech
6. **Persistent Storage**: SQLite database for all data
7. **Bookmark System**: Save and organize articles
8. **Combined Summaries**: Generate summaries from multiple articles

## Troubleshooting

- **Port busy**: Use `./start.sh --port 8080`
- **Permission denied**: Run `chmod +x *.sh`
- **Python not found**: Install with `sudo apt install python3.11`
- **No API key**: Check `.env` file has `GEMINI_API_KEY=your_key`
- **Database errors**: Database auto-creates in `data/` directory

## Security Notes

- Keep your `GEMINI_API_KEY` secure and never share it
- Use `--host 127.0.0.1` to restrict access to localhost only
- Consider running behind nginx for production use

## System Service (Optional)

To run as a background service:

```bash
# Edit the service template
nano ~/rss-reader/rss-reader.service

# Install as system service
sudo cp ~/rss-reader/rss-reader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rss-reader
sudo systemctl start rss-reader
```

## Support

Everything is designed to work automatically. If you encounter issues:
1. Check the terminal output for error messages
2. Verify your API key is set correctly in `.env`
3. Ensure the port isn't already in use
4. Check file permissions with `ls -la`

Your RSS Reader deployment package is ready for your Debian server!