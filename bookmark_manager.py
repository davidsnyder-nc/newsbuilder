import streamlit as st
from typing import List, Dict

class BookmarkManager:
    def __init__(self):
        if 'bookmarks' not in st.session_state:
            st.session_state.bookmarks = []
        if 'bookmarked_links' not in st.session_state:
            st.session_state.bookmarked_links = set()
    
    def add_bookmark(self, article: Dict):
        """Add an article to bookmarks"""
        if article['link'] not in st.session_state.bookmarked_links:
            st.session_state.bookmarks.append(article)
            st.session_state.bookmarked_links.add(article['link'])
    
    def remove_bookmark(self, link: str):
        """Remove an article from bookmarks by link"""
        if link in st.session_state.bookmarked_links:
            st.session_state.bookmarks = [
                bookmark for bookmark in st.session_state.bookmarks 
                if bookmark['link'] != link
            ]
            st.session_state.bookmarked_links.remove(link)
    
    def is_bookmarked(self, link: str) -> bool:
        """Check if an article is bookmarked"""
        return link in st.session_state.bookmarked_links
    
    def get_bookmarks(self) -> List[Dict]:
        """Get all bookmarked articles"""
        return st.session_state.bookmarks
    
    def clear_bookmarks(self):
        """Clear all bookmarks"""
        st.session_state.bookmarks = []
        st.session_state.bookmarked_links = set()
    
    def get_bookmark_count(self) -> int:
        """Get the number of bookmarked articles"""
        return len(st.session_state.bookmarks)
