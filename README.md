# RSS Reader with AI Summarization

A powerful RSS feed reader that combines AI-driven summarization, multi-source news aggregation, and intelligent content parsing with enhanced user interaction capabilities.

## Features

- **RSS Feed Management**: Add, remove, and manage multiple RSS feeds
- **AI-Powered Summarization**: Generate summaries using Google Gemini AI
- **Text-to-Speech**: Convert summaries to high-quality audio using Google Cloud TTS
- **Article Scraping**: Fetch full article content from original sources
- **Bookmark System**: Save and organize articles for later reading
- **Combined Summaries**: Create comprehensive summaries from multiple articles
- **Clean Material Design Interface**: Professional, icon-free interface
- **Persistent Storage**: SQLite database for feeds, articles, and bookmarks

## Technology Stack

- **Frontend**: Streamlit web interface
- **Backend**: Python with modular architecture
- **Database**: SQLite for persistent storage
- **AI Services**: Google Gemini for summarization and TTS
- **Web Scraping**: Trafilatura for content extraction
- **Audio Processing**: Google Cloud Text-to-Speech

## Installation

### Quick Start (Recommended)

1. **Download and extract the project**:
   ```bash
   # If you have the deployment package
   tar -xzf rss-reader-deployment.tar.gz
   cd rss-reader-deployment
   
   # Or clone from GitHub
   git clone [repository-url]
   cd rss-reader
   ```

2. **Set up virtual environment and dependencies**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install all required packages
   pip install -r install-requirements.txt
   ```

3. **Start the application**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Manual Installation (if requirements file doesn't work)

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

2. **Install dependencies individually**:
   ```bash
   pip install streamlit>=1.46.1
   pip install feedparser>=6.0.11
   pip install google-genai>=1.23.0
   pip install google-cloud-texttospeech>=2.27.0
   pip install pydub>=0.25.1
   pip install requests>=2.32.4
   pip install trafilatura>=2.0.0
   ```

3. **Start the application**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

## Configuration

### API Key Setup

**No .env file needed!** The RSS Reader uses web-based configuration:

1. Start the application: `./start.sh`
2. Open browser to `http://localhost:5000` (or `http://your-server-ip:5000`)
3. Go to "Settings" page
4. Expand "Configure API Keys" 
5. Enter your Gemini API key from [Google AI Studio](https://aistudio.google.com/)
6. Click "Save API Key"

The API key is stored securely in the database and persists across sessions.

### Optional: Environment Variables

If you prefer using environment variables, create a `.env` file:

```bash
# Optional: Google Gemini API Key (can also be set via web interface)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Custom port (default is 5000)
PORT=5000

# Optional: Host binding (default is 0.0.0.0)
HOST=0.0.0.0
```

## Usage

### Starting the Application

```bash
# Start on default port 5000
./start.sh

# Start on custom port
./start.sh --port 8080

# Start on specific host
./start.sh --host 127.0.0.1

# Show help
./start.sh --help
```

### Stopping the Application

```bash
./stop.sh
```

### Accessing the Application

Once started, open your web browser and navigate to:
- Local access: `http://localhost:5000`
- Network access: `http://your-server-ip:5000`

**Note**: If you see a directory listing instead of the RSS Reader, make sure you're accessing port 5000, not the default web port 80.

### Using the RSS Reader

1. **Add RSS Feeds**: Go to the "RSS Feeds" page and add your favorite news sources
2. **Browse Articles**: View articles from all feeds on the main page
3. **Bookmark Articles**: Save interesting articles for later reading
4. **Generate Summaries**: Create AI-powered summaries of articles or combined summaries from bookmarks
5. **Text-to-Speech**: Convert summaries to audio for hands-free consumption

## System Service (Optional)

To run as a system service, edit the provided service template:

```bash
# Edit the service file
nano ~/rss-reader/rss-reader.service

# Update paths and username, then:
sudo cp ~/rss-reader/rss-reader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rss-reader
sudo systemctl start rss-reader
```

## Directory Structure

```
~/rss-reader/
├── app/                    # Application files
│   ├── app.py             # Main Streamlit application
│   ├── ai_summarizer.py   # AI summarization module
│   ├── article_scraper.py # Web scraping module
│   ├── audio_processor.py # Text-to-speech module
│   ├── bookmark_manager.py# Bookmark management
│   ├── database.py        # Database operations
│   └── rss_manager.py     # RSS feed management
├── data/                  # Database and user data
│   └── rss_reader.db     # SQLite database
├── logs/                  # Application logs
├── venv/                  # Python virtual environment
├── .env                   # Environment variables
├── start.sh              # Startup script
├── stop.sh               # Stop script
└── requirements.txt      # Python dependencies
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError (trafilatura, streamlit, etc.)**:
   ```bash
   source venv/bin/activate
   pip install -r install-requirements.txt
   ```

2. **Directory listing instead of RSS Reader**:
   - Make sure you're accessing `http://your-server-ip:5000` (not port 80)
   - The RSS Reader runs on port 5000, not the default web port

3. **Port already in use**:
   ```bash
   ./start.sh --port 8080  # Use different port
   ```

4. **Permission denied**:
   ```bash
   chmod +x start.sh stop.sh
   ```

5. **Virtual environment not found**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r install-requirements.txt
   ```

6. **API key not working**: Configure via Settings page in web interface, not .env file

### Logs

Application logs are available in:
- Streamlit logs: Check terminal output
- Database errors: Displayed in the web interface
- System logs: `/var/log/syslog` (if running as service)

## Security Considerations

- Keep your `GEMINI_API_KEY` secret and never commit it to version control
- Run the application behind a reverse proxy (nginx) for production use
- Consider using HTTPS in production environments
- Regularly update dependencies for security patches

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review application logs for error details
- Ensure all dependencies are properly installed
- Verify your API key is correctly configured