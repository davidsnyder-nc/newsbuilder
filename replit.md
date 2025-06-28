# RSS Reader with AI Summarization

## Overview

This is a Python-based RSS feed reader application built with Streamlit that incorporates AI-powered article summarization and text-to-speech functionality. The application allows users to manage RSS feeds, scrape full article content, generate AI summaries using Google's Gemini model, bookmark articles, and convert text to speech using Google Cloud TTS.

## System Architecture

The application follows a modular architecture with distinct components handling different aspects of functionality:

- **Frontend**: Streamlit web interface providing an interactive user experience
- **RSS Management**: Custom RSS feed parsing and management system
- **Content Extraction**: Web scraping for full article content using Trafilatura
- **AI Processing**: Google Gemini integration for intelligent text summarization
- **Audio Generation**: Google Cloud Text-to-Speech for audio content creation
- **Data Management**: Session-based storage for feeds, articles, and bookmarks

## Key Components

### Core Modules

1. **RSSManager** (`rss_manager.py`)
   - Handles RSS feed addition, removal, and parsing
   - Uses feedparser library for RSS content extraction
   - Stores feed data in Streamlit session state
   - Validates feed URLs before addition

2. **ArticleScraper** (`article_scraper.py`)
   - Extracts full article content from URLs using Trafilatura
   - Provides clean, readable text extraction
   - Supports batch processing of multiple articles
   - Includes metadata extraction capabilities

3. **AISummarizer** (`ai_summarizer.py`)
   - Integrates with Google Gemini 2.5-flash model for text summarization
   - Supports both individual and combined article summarization
   - Uses environment variables for API key management
   - Implements error handling for API failures

4. **AudioProcessor** (`audio_processor.py`)
   - Converts text to speech using Google Cloud TTS
   - Supports long text processing with chunking
   - Uses high-quality neural voices
   - Handles temporary file management for audio output

5. **BookmarkManager** (`bookmark_manager.py`)
   - Manages article bookmarking functionality
   - Prevents duplicate bookmarks
   - Provides bookmark persistence through session state
   - Supports bookmark removal and clearing

### Main Application (`app.py`)

The main Streamlit application orchestrates all components and provides:
- Session state initialization for all managers
- Sidebar RSS feed management interface
- Main content area for article display and interaction
- Integration points for all core functionalities

## Data Flow

1. **RSS Feed Addition**: User adds RSS URL → RSSManager validates and parses → Articles stored in session state
2. **Article Scraping**: User selects article → ArticleScraper extracts full content → Content available for processing
3. **AI Summarization**: Full article content → AISummarizer processes via Gemini API → Summary generated
4. **Audio Generation**: Text content → AudioProcessor converts via Google TTS → Audio file created
5. **Bookmark Management**: User bookmarks article → BookmarkManager stores in session state → Available in bookmark list

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework
- **feedparser**: RSS feed parsing
- **trafilatura**: Web content extraction
- **google-genai**: Google Gemini AI integration
- **google-cloud-texttospeech**: Google Cloud TTS
- **pydub**: Audio processing
- **requests**: HTTP requests

### External Services
- **Google Gemini API**: AI text summarization
- **Google Cloud Text-to-Speech**: Audio generation

### Environment Variables
- `GEMINI_API_KEY`: Required for AI summarization functionality
- `GOOGLE_APPLICATION_CREDENTIALS`: Required for Google Cloud TTS authentication

## Deployment Strategy

The application is designed for:
- **Local Development**: Direct Python/Streamlit execution
- **Cloud Deployment**: Compatible with Streamlit Cloud, Heroku, or similar platforms
- **Container Deployment**: Can be containerized with Docker
- **Replit Deployment**: Optimized for Replit environment with session-based storage

Key deployment considerations:
- Environment variables must be configured for AI services
- No persistent database required (uses session state)
- Internet access required for RSS feeds and external APIs
- Google Cloud credentials needed for TTS functionality

## Changelog

- June 28, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.