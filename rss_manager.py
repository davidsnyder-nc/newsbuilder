import feedparser
from datetime import datetime
from typing import Dict, List, Optional
from database import DatabaseManager

class RSSManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def add_feed(self, name: str, url: str) -> bool:
        """Add a new RSS feed"""
        try:
            # Test if the feed is valid
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                return False
            
            # Add to database
            if self.db.add_rss_feed(name, url):
                self.refresh_feed(name, url)
                return True
            return False
        except Exception as e:
            print(f"Error adding feed: {str(e)}")
            return False
    
    def remove_feed(self, name: str):
        """Remove an RSS feed"""
        self.db.remove_rss_feed(name)
    
    def get_feeds(self) -> Dict[str, str]:
        """Get all RSS feeds"""
        feeds = self.db.get_rss_feeds()
        return {feed['name']: feed['url'] for feed in feeds}
    
    def get_feeds_detailed(self) -> List[Dict]:
        """Get detailed feed information"""
        return self.db.get_rss_feeds()
    
    def refresh_feed(self, name: str, url: str):
        """Refresh a single RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries:
                # Extract image URLs from various RSS fields
                image_url = None
                
                # Try to get image from media:content
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if media.get('medium') == 'image' or 'image' in media.get('type', ''):
                            image_url = media.get('url')
                            break
                
                # Try to get image from enclosures
                if not image_url and hasattr(entry, 'enclosures'):
                    for enclosure in entry.enclosures:
                        if enclosure.type and 'image' in enclosure.type:
                            image_url = enclosure.href
                            break
                
                # Try to get image from media:thumbnail
                if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get('url')
                
                # Try to extract image from content or summary using basic regex
                if not image_url:
                    import re
                    content_to_search = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                    content_to_search += ' ' + entry.get('summary', '')
                    
                    # Look for img tags
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_to_search)
                    if img_match:
                        image_url = img_match.group(1)
                
                article = {
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'feed_name': name,
                    'guid': entry.get('guid', entry.get('link', '')),
                    'image_url': image_url
                }
                articles.append(article)
            
            # Save articles to database
            self.db.save_articles(name, articles)
            self.db.update_feed_refresh_time(name)
            
        except Exception as e:
            print(f"Error refreshing feed {name}: {str(e)}")
    
    def refresh_all_feeds(self):
        """Refresh all RSS feeds"""
        feeds = self.db.get_rss_feeds()
        for feed in feeds:
            self.refresh_feed(feed['name'], feed['url'])
    
    def get_articles(self, feed_name: str) -> List[Dict]:
        """Get articles from a specific feed"""
        return self.db.get_articles(feed_name)
    
    def get_all_articles(self) -> List[Dict]:
        """Get all articles from all feeds, sorted by publication date"""
        return self.db.get_articles()
