import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "rss_reader.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RSS feeds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_refreshed TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Articles table (cached RSS articles)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                summary TEXT,
                published TEXT,
                guid TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES rss_feeds (id)
            )
        ''')
        
        # Add image_url column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE articles ADD COLUMN image_url TEXT')
        except:
            pass  # Column already exists
        
        # Bookmarks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                summary TEXT,
                published TEXT,
                feed_name TEXT,
                image_url TEXT,
                bookmarked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add image_url column to bookmarks if it doesn't exist
        try:
            cursor.execute('ALTER TABLE bookmarks ADD COLUMN image_url TEXT')
        except:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # Settings methods
    def save_setting(self, key: str, value: Any):
        """Save a setting to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert value to JSON string if it's not a simple type
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, str(value)))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default=None):
        """Get a setting from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            value = result[0]
            # Try to parse as JSON
            try:
                return json.loads(value)
            except:
                return value
        
        return default
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM settings')
        results = cursor.fetchall()
        
        conn.close()
        
        settings = {}
        for key, value in results:
            try:
                settings[key] = json.loads(value)
            except:
                settings[key] = value
        
        return settings
    
    # RSS Feeds methods
    def add_rss_feed(self, name: str, url: str) -> bool:
        """Add a new RSS feed"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rss_feeds (name, url)
                VALUES (?, ?)
            ''', (name, url))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Feed name already exists
    
    def remove_rss_feed(self, name: str):
        """Remove an RSS feed and its articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get feed ID
        cursor.execute('SELECT id FROM rss_feeds WHERE name = ?', (name,))
        result = cursor.fetchone()
        
        if result:
            feed_id = result[0]
            # Delete articles for this feed
            cursor.execute('DELETE FROM articles WHERE feed_id = ?', (feed_id,))
            # Delete the feed
            cursor.execute('DELETE FROM rss_feeds WHERE name = ?', (name,))
        
        conn.commit()
        conn.close()
    
    def get_rss_feeds(self) -> List[Dict]:
        """Get all RSS feeds"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, url, created_at, last_refreshed, active
            FROM rss_feeds
            WHERE active = 1
            ORDER BY name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        feeds = []
        for row in results:
            feeds.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'created_at': row[3],
                'last_refreshed': row[4],
                'active': row[5]
            })
        
        return feeds
    
    def update_feed_refresh_time(self, name: str):
        """Update the last refresh time for a feed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE rss_feeds 
            SET last_refreshed = CURRENT_TIMESTAMP 
            WHERE name = ?
        ''', (name,))
        
        conn.commit()
        conn.close()
    
    # Articles methods
    def save_articles(self, feed_name: str, articles: List[Dict]):
        """Save articles for a feed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get feed ID
        cursor.execute('SELECT id FROM rss_feeds WHERE name = ?', (feed_name,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return
        
        feed_id = result[0]
        
        # Clear existing articles for this feed
        cursor.execute('DELETE FROM articles WHERE feed_id = ?', (feed_id,))
        
        # Insert new articles
        for article in articles:
            try:
                cursor.execute('''
                    INSERT INTO articles (feed_id, title, link, summary, published, guid, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    feed_id,
                    article.get('title', ''),
                    article.get('link', ''),
                    article.get('summary', ''),
                    article.get('published', ''),
                    article.get('guid', ''),
                    article.get('image_url', None)
                ))
            except sqlite3.IntegrityError:
                # Skip duplicate articles
                continue
        
        conn.commit()
        conn.close()
    
    def get_articles(self, feed_name: str = None) -> List[Dict]:
        """Get articles, optionally filtered by feed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if feed_name:
            cursor.execute('''
                SELECT a.title, a.link, a.summary, a.published, a.guid, f.name as feed_name, a.image_url
                FROM articles a
                JOIN rss_feeds f ON a.feed_id = f.id
                WHERE f.name = ?
                ORDER BY a.created_at DESC
            ''', (feed_name,))
        else:
            cursor.execute('''
                SELECT a.title, a.link, a.summary, a.published, a.guid, f.name as feed_name, a.image_url
                FROM articles a
                JOIN rss_feeds f ON a.feed_id = f.id
                ORDER BY a.created_at DESC
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in results:
            articles.append({
                'title': row[0],
                'link': row[1],
                'summary': row[2],
                'published': row[3],
                'guid': row[4],
                'feed_name': row[5],
                'image_url': row[6]
            })
        
        return articles
    
    # Bookmarks methods
    def add_bookmark(self, article: Dict) -> bool:
        """Add an article to bookmarks"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bookmarks (title, link, summary, published, feed_name, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title', ''),
                article.get('link', ''),
                article.get('summary', ''),
                article.get('published', ''),
                article.get('feed_name', ''),
                article.get('image_url', None)
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Already bookmarked
    
    def remove_bookmark(self, link: str):
        """Remove a bookmark"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM bookmarks WHERE link = ?', (link,))
        
        conn.commit()
        conn.close()
    
    def is_bookmarked(self, link: str) -> bool:
        """Check if an article is bookmarked"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM bookmarks WHERE link = ?', (link,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def get_bookmarks(self) -> List[Dict]:
        """Get all bookmarked articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, link, summary, published, feed_name, bookmarked_at
            FROM bookmarks
            ORDER BY bookmarked_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        bookmarks = []
        for row in results:
            bookmarks.append({
                'title': row[0],
                'link': row[1],
                'summary': row[2],
                'published': row[3],
                'feed_name': row[4],
                'bookmarked_at': row[5]
            })
        
        return bookmarks
    
    def clear_bookmarks(self):
        """Clear all bookmarks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM bookmarks')
        
        conn.commit()
        conn.close()
    
    def get_bookmark_count(self) -> int:
        """Get the number of bookmarked articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM bookmarks')
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else 0