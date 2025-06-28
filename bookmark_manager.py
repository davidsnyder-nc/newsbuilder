from typing import List, Dict
from database import DatabaseManager

class BookmarkManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def add_bookmark(self, article: Dict) -> bool:
        """Add an article to bookmarks"""
        return self.db.add_bookmark(article)
    
    def remove_bookmark(self, link: str):
        """Remove an article from bookmarks by link"""
        self.db.remove_bookmark(link)
    
    def is_bookmarked(self, link: str) -> bool:
        """Check if an article is bookmarked"""
        return self.db.is_bookmarked(link)
    
    def get_bookmarks(self) -> List[Dict]:
        """Get all bookmarked articles"""
        return self.db.get_bookmarks()
    
    def clear_bookmarks(self):
        """Clear all bookmarks"""
        self.db.clear_bookmarks()
    
    def get_bookmark_count(self) -> int:
        """Get the number of bookmarked articles"""
        return self.db.get_bookmark_count()
