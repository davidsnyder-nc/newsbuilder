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

## Installation on Debian/Ubuntu

### Automatic Installation

1. **Download and run the installation script**:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/rss-reader/main/install.sh
   chmod +x install.sh
   ./install.sh
   ```

2. **Set up your API key**:
   ```bash
   cd ~/rss-reader
   cp .env.template .env
   nano .env  # Add your GEMINI_API_KEY
   ```

3. **Deploy the application files**:
   ```bash
   # If you have the source files
   ./deploy.sh
   ```

### Manual Installation

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev
   sudo apt install -y git curl wget build-essential
   ```

2. **Create project directory and virtual environment**:
   ```bash
   mkdir ~/rss-reader
   cd ~/rss-reader
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install --upgrade pip
   pip install streamlit==1.39.0 feedparser==6.0.11 google-genai==0.8.3
   pip install google-cloud-texttospeech==2.17.2 pydub==0.25.1
   pip install requests==2.32.3 trafilatura==1.12.2
   ```

4. **Copy application files** to `~/rss-reader/app/`

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Custom port (default is 5000)
PORT=5000

# Optional: Host binding (default is 0.0.0.0)
HOST=0.0.0.0
```

### Getting API Keys

1. **Google Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Add it to your `.env` file

## Usage

### Starting the Application

```bash
cd ~/rss-reader

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

1. **Port already in use**:
   ```bash
   ./start.sh --port 8080  # Use different port
   ```

2. **Permission denied**:
   ```bash
   chmod +x start.sh stop.sh
   ```

3. **Python not found**:
   ```bash
   sudo apt install python3.11 python3.11-pip
   ```

4. **Database errors**: The database is automatically created in the `data/` directory

5. **Missing API key**: Check your `.env` file and ensure `GEMINI_API_KEY` is set

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