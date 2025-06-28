import streamlit as st
import os
from datetime import datetime
from rss_manager import RSSManager
from bookmark_manager import BookmarkManager
from article_scraper import ArticleScraper
from ai_summarizer import AISummarizer
from audio_processor import AudioProcessor

# Initialize session state
if 'rss_manager' not in st.session_state:
    st.session_state.rss_manager = RSSManager()

if 'bookmark_manager' not in st.session_state:
    st.session_state.bookmark_manager = BookmarkManager()

if 'article_scraper' not in st.session_state:
    st.session_state.article_scraper = ArticleScraper()

if 'ai_summarizer' not in st.session_state:
    st.session_state.ai_summarizer = AISummarizer()

if 'audio_processor' not in st.session_state:
    st.session_state.audio_processor = AudioProcessor()

# Page configuration
st.set_page_config(
    page_title="RSS Reader with AI Summarization",
    page_icon="📰",
    layout="wide"
)

st.title("📰 RSS Feed Reader with AI Summarization")

# Sidebar for RSS feed management
with st.sidebar:
    st.header("RSS Feed Management")
    
    # Add new RSS feed
    with st.expander("Add RSS Feed"):
        feed_name = st.text_input("Feed Name")
        feed_url = st.text_input("RSS URL")
        if st.button("Add Feed"):
            if feed_name and feed_url:
                success = st.session_state.rss_manager.add_feed(feed_name, feed_url)
                if success:
                    st.success(f"Added feed: {feed_name}")
                    st.rerun()
                else:
                    st.error("Failed to add feed. Please check the URL.")
            else:
                st.error("Please provide both name and URL")
    
    # Display current feeds
    st.subheader("Current Feeds")
    feeds = st.session_state.rss_manager.get_feeds()
    for feed_name in feeds:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(feed_name)
        with col2:
            if st.button("🗑️", key=f"delete_{feed_name}"):
                st.session_state.rss_manager.remove_feed(feed_name)
                st.rerun()
    
    st.divider()
    
    # Bookmark management
    st.header("Bookmarks")
    bookmarks = st.session_state.bookmark_manager.get_bookmarks()
    st.text(f"Total bookmarks: {len(bookmarks)}")
    
    if bookmarks:
        if st.button("📝 Generate Combined Summary"):
            st.session_state.show_summary_tab = True
            st.rerun()
        
        if st.button("🗑️ Clear All Bookmarks"):
            st.session_state.bookmark_manager.clear_bookmarks()
            st.success("All bookmarks cleared!")
            st.rerun()

# Main content area
tab1, tab2, tab3 = st.tabs(["📰 Feed Articles", "🔖 Bookmarked Articles", "📄 Combined Summary"])

with tab1:
    st.header("RSS Feed Articles")
    
    if feeds:
        # Refresh feeds button
        if st.button("🔄 Refresh All Feeds"):
            with st.spinner("Refreshing feeds..."):
                st.session_state.rss_manager.refresh_all_feeds()
            st.success("Feeds refreshed!")
            st.rerun()
        
        # Display articles from all feeds
        all_articles = st.session_state.rss_manager.get_all_articles()
        
        if all_articles:
            st.text(f"Total articles: {len(all_articles)}")
            
            for article in all_articles[:50]:  # Limit to 50 most recent articles
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.subheader(article['title'])
                        st.text(f"Source: {article['feed_name']}")
                        if article['published']:
                            st.text(f"Published: {article['published']}")
                        
                        if article['summary']:
                            st.write(article['summary'][:300] + "..." if len(article['summary']) > 300 else article['summary'])
                        
                        if article['link']:
                            st.link_button("Read Full Article", article['link'])
                    
                    with col2:
                        is_bookmarked = st.session_state.bookmark_manager.is_bookmarked(article['link'])
                        bookmark_text = "Remove Bookmark" if is_bookmarked else "Bookmark"
                        bookmark_icon = "🔖" if is_bookmarked else "📌"
                        
                        if st.button(f"{bookmark_icon} {bookmark_text}", key=f"bookmark_{article['link']}"):
                            if is_bookmarked:
                                st.session_state.bookmark_manager.remove_bookmark(article['link'])
                                st.success("Bookmark removed!")
                            else:
                                st.session_state.bookmark_manager.add_bookmark(article)
                                st.success("Article bookmarked!")
                            st.rerun()
                
                st.divider()
        else:
            st.info("No articles found. Try refreshing the feeds.")
    else:
        st.info("No RSS feeds added yet. Add some feeds in the sidebar to get started!")

with tab2:
    st.header("Bookmarked Articles")
    
    bookmarks = st.session_state.bookmark_manager.get_bookmarks()
    
    if bookmarks:
        for bookmark in bookmarks:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.subheader(bookmark['title'])
                    st.text(f"Source: {bookmark['feed_name']}")
                    if bookmark['published']:
                        st.text(f"Published: {bookmark['published']}")
                    
                    if bookmark['summary']:
                        st.write(bookmark['summary'][:300] + "..." if len(bookmark['summary']) > 300 else bookmark['summary'])
                    
                    if bookmark['link']:
                        st.link_button("Read Full Article", bookmark['link'])
                
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_bookmark_{bookmark['link']}"):
                        st.session_state.bookmark_manager.remove_bookmark(bookmark['link'])
                        st.success("Bookmark removed!")
                        st.rerun()
            
            st.divider()
    else:
        st.info("No bookmarked articles yet. Bookmark some articles from the feed to see them here!")

with tab3:
    st.header("Combined Summary")
    
    bookmarks = st.session_state.bookmark_manager.get_bookmarks()
    
    if bookmarks:
        if st.button("🤖 Generate AI Summary"):
            with st.spinner("Fetching full articles and generating summary..."):
                try:
                    # Fetch full article content for all bookmarks
                    full_articles = []
                    progress_bar = st.progress(0)
                    
                    for i, bookmark in enumerate(bookmarks):
                        try:
                            full_content = st.session_state.article_scraper.scrape_article(bookmark['link'])
                            if full_content:
                                full_articles.append({
                                    'title': bookmark['title'],
                                    'content': full_content,
                                    'source': bookmark['feed_name']
                                })
                        except Exception as e:
                            st.warning(f"Failed to scrape article: {bookmark['title']}")
                        
                        progress_bar.progress((i + 1) / len(bookmarks))
                    
                    if full_articles:
                        # Generate combined summary
                        combined_summary = st.session_state.ai_summarizer.create_combined_summary(full_articles)
                        
                        if combined_summary:
                            st.session_state.combined_summary = combined_summary
                            st.success("Summary generated successfully!")
                        else:
                            st.error("Failed to generate summary")
                    else:
                        st.error("No articles could be scraped for summarization")
                        
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
        
        # Display generated summary
        if hasattr(st.session_state, 'combined_summary') and st.session_state.combined_summary:
            st.subheader("Generated Summary")
            
            # Text display
            st.text_area("Combined Summary", st.session_state.combined_summary, height=300)
            
            # Copy to clipboard button
            st.code(st.session_state.combined_summary)
            
            # Audio generation and playback
            st.subheader("Audio Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔊 Generate Audio"):
                    with st.spinner("Generating audio..."):
                        try:
                            audio_file = st.session_state.audio_processor.text_to_speech(st.session_state.combined_summary)
                            if audio_file:
                                st.session_state.audio_file = audio_file
                                st.success("Audio generated successfully!")
                            else:
                                st.error("Failed to generate audio")
                        except Exception as e:
                            st.error(f"Error generating audio: {str(e)}")
            
            with col2:
                if hasattr(st.session_state, 'audio_file') and st.session_state.audio_file:
                    st.audio(st.session_state.audio_file, format='audio/mp3')
            
            with col3:
                if hasattr(st.session_state, 'audio_file') and st.session_state.audio_file:
                    with open(st.session_state.audio_file, 'rb') as f:
                        audio_data = f.read()
                    st.download_button(
                        label="📥 Download MP3",
                        data=audio_data,
                        file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                        mime="audio/mp3"
                    )
    else:
        st.info("No bookmarked articles to summarize. Bookmark some articles first!")

# Footer
st.divider()
st.caption("RSS Reader with AI Summarization - Powered by Streamlit, Gemini AI, and Google TTS")
