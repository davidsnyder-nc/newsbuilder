import feedparser
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional

class RSSManager:
    def __init__(self):
        if 'rss_feeds' not in st.session_state:
            st.session_state.rss_feeds = {}
        if 'rss_articles' not in st.session_state:
            st.session_state.rss_articles = {}
    
    def add_feed(self, name: str, url: str) -> bool:
        """Add a new RSS feed"""
        try:
            # Test if the feed is valid
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                return False
            
            st.session_state.rss_feeds[name] = url
            self.refresh_feed(name, url)
            return True
        except Exception as e:
            st.error(f"Error adding feed: {str(e)}")
            return False
    
    def remove_feed(self, name: str):
        """Remove an RSS feed"""
        if name in st.session_state.rss_feeds:
            del st.session_state.rss_feeds[name]
        if name in st.session_state.rss_articles:
            del st.session_state.rss_articles[name]
    
    def get_feeds(self) -> Dict[str, str]:
        """Get all RSS feeds"""
        return st.session_state.rss_feeds
    
    def refresh_feed(self, name: str, url: str):
        """Refresh a single RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'feed_name': name,
                    'guid': entry.get('guid', entry.get('link', ''))
                }
                articles.append(article)
            
            st.session_state.rss_articles[name] = articles
            
        except Exception as e:
            st.error(f"Error refreshing feed {name}: {str(e)}")
    
    def refresh_all_feeds(self):
        """Refresh all RSS feeds"""
        for name, url in st.session_state.rss_feeds.items():
            self.refresh_feed(name, url)
    
    def get_articles(self, feed_name: str) -> List[Dict]:
        """Get articles from a specific feed"""
        return st.session_state.rss_articles.get(feed_name, [])
    
    def get_all_articles(self) -> List[Dict]:
        """Get all articles from all feeds, sorted by publication date"""
        all_articles = []
        
        for feed_name in st.session_state.rss_articles:
            articles = st.session_state.rss_articles[feed_name]
            all_articles.extend(articles)
        
        # Sort by published date (most recent first)
        def get_sort_key(article):
            try:
                if article['published']:
                    # Try to parse the date
                    parsed = feedparser._parse_date(article['published'])
                    if parsed:
                        return datetime(*parsed[:6])
                return datetime.min
            except:
                return datetime.min
        
        all_articles.sort(key=get_sort_key, reverse=True)
        return all_articles
