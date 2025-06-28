import streamlit as st
import os
from datetime import datetime
from rss_manager import RSSManager
from bookmark_manager import BookmarkManager
from article_scraper import ArticleScraper
from ai_summarizer import AISummarizer
from audio_processor import AudioProcessor
from database import DatabaseManager
from svg_icons import get_svg_icon, svg_icon_html

# Configure page
st.set_page_config(
    page_title="RSS Reader with AI Summarization",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and managers
@st.cache_resource
def get_managers():
    """Initialize all managers with caching"""
    db = DatabaseManager()
    rss_manager = RSSManager()
    bookmark_manager = BookmarkManager()
    article_scraper = ArticleScraper()
    ai_summarizer = AISummarizer()
    audio_processor = AudioProcessor()
    
    return db, rss_manager, bookmark_manager, article_scraper, ai_summarizer, audio_processor

# Get managers
db, rss_manager, bookmark_manager, article_scraper, ai_summarizer, audio_processor = get_managers()

# Navigation
st.sidebar.markdown(f'<h1 style="margin: 0;">{svg_icon_html("rss", 24)} RSS Reader</h1>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation menu
pages = {
    "📖 Read Articles": "articles",
    "📊 RSS Feeds": "feeds", 
    "🔖 Bookmarks": "bookmarks",
    "📄 Summary": "summary",
    "⚙️ Settings": "settings"
}

# Use query params for navigation
query_params = st.query_params
current_page = query_params.get("page", "articles")

# Navigation buttons
for page_name, page_key in pages.items():
    if st.sidebar.button(page_name, key=f"nav_{page_key}", use_container_width=True):
        st.query_params["page"] = page_key
        st.rerun()

# Quick stats in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(f'<h3>{svg_icon_html("chart", 20)} Quick Stats</h3>', unsafe_allow_html=True)

feeds_count = len(rss_manager.get_feeds())
bookmarks_count = bookmark_manager.get_bookmark_count()

st.sidebar.metric("RSS Feeds", feeds_count)
st.sidebar.metric("Bookmarks", bookmarks_count)

if feeds_count > 0:
    if st.sidebar.button("🔄 Refresh All Feeds", use_container_width=True):
        with st.spinner("Refreshing feeds..."):
            rss_manager.refresh_all_feeds()
        st.success("Feeds refreshed!")
        st.rerun()

# Page content
if current_page == "articles":
    st.markdown(f'<h1>{svg_icon_html("articles", 32)} RSS Articles</h1>', unsafe_allow_html=True)
    
    feeds = rss_manager.get_feeds()
    
    if not feeds:
        st.info("No RSS feeds added yet. Go to RSS Feeds page to add some feeds!")
    else:
        # Display articles
        all_articles = rss_manager.get_all_articles()
        
        if not all_articles:
            st.info("No articles found. Try refreshing the feeds.")
        else:
            # Filter options
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_feed = st.selectbox(
                    "Filter by feed:",
                    ["All Feeds"] + list(feeds.keys()),
                    key="feed_filter"
                )
            with col2:
                articles_per_page = st.selectbox("Articles per page:", [10, 25, 50, 100], index=1)
            
            # Filter articles
            if selected_feed != "All Feeds":
                filtered_articles = [a for a in all_articles if a['feed_name'] == selected_feed]
            else:
                filtered_articles = all_articles
            
            st.write(f"Showing {len(filtered_articles[:articles_per_page])} of {len(filtered_articles)} articles")
            
            # Display articles
            for article in filtered_articles[:articles_per_page]:
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.subheader(article['title'])
                        st.caption(f"📡 {article['feed_name']} • {article.get('published', 'No date')}")
                        
                        if article['summary']:
                            st.write(article['summary'][:200] + "..." if len(article['summary']) > 200 else article['summary'])
                        
                        if article['link']:
                            st.link_button("🔗 Read Full Article", article['link'])
                    
                    with col2:
                        is_bookmarked = bookmark_manager.is_bookmarked(article['link'])
                        
                        if is_bookmarked:
                            if st.button("🔖 Bookmarked", key=f"bookmark_{article['link']}", disabled=True):
                                pass
                        else:
                            if st.button("📌 Bookmark", key=f"bookmark_{article['link']}"):
                                if bookmark_manager.add_bookmark(article):
                                    st.success("Article bookmarked!")
                                    st.rerun()
                                else:
                                    st.error("Failed to bookmark article")
                
                st.divider()

elif current_page == "feeds":
    st.markdown(f'<h1>{svg_icon_html("feeds", 32)} RSS Feed Management</h1>', unsafe_allow_html=True)
    
    # Add new feed section
    with st.expander(f"{svg_icon_html('add', 16)} Add New RSS Feed", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            feed_name = st.text_input("Feed Name", placeholder="e.g., BBC News")
        with col2:
            feed_url = st.text_input("RSS URL", placeholder="https://example.com/rss")
        with col3:
            st.write("")  # Spacing
            if st.button("Add Feed", type="primary"):
                if feed_name and feed_url:
                    with st.spinner("Adding and testing feed..."):
                        success = rss_manager.add_feed(feed_name, feed_url)
                    if success:
                        st.success(f"Added feed: {feed_name}")
                        st.rerun()
                    else:
                        st.error("Failed to add feed. Please check the URL and try again.")
                else:
                    st.error("Please provide both name and URL")
    
    # Display current feeds
    st.markdown(f'<h3>{svg_icon_html("feeds", 24)} Current RSS Feeds</h3>', unsafe_allow_html=True)
    
    feeds = rss_manager.get_feeds_detailed()
    
    if not feeds:
        st.info("No RSS feeds added yet. Add your first feed above!")
    else:
        for feed in feeds:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{feed['name']}**")
                    st.caption(feed['url'])
                
                with col2:
                    articles_count = len(rss_manager.get_articles(feed['name']))
                    st.metric("Articles", articles_count)
                
                with col3:
                    if feed['last_refreshed']:
                        st.caption(f"Last updated: {feed['last_refreshed'][:19]}")
                    else:
                        st.caption("Never refreshed")
                
                with col4:
                    if st.button("🗑️", key=f"delete_{feed['name']}", help="Delete feed"):
                        rss_manager.remove_feed(feed['name'])
                        st.success(f"Deleted feed: {feed['name']}")
                        st.rerun()
            
            st.divider()

elif current_page == "bookmarks":
    st.markdown(f'<h1>{svg_icon_html("bookmark", 32)} Bookmarked Articles</h1>', unsafe_allow_html=True)
    
    bookmarks = bookmark_manager.get_bookmarks()
    
    if not bookmarks:
        st.info("No bookmarked articles yet. Bookmark some articles from the RSS feeds to see them here!")
    else:
        # Actions section
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📝 Generate Combined Summary", type="primary", use_container_width=True):
                st.query_params["page"] = "summary"
                st.rerun()
        with col2:
            if st.button("🗑️ Clear All Bookmarks", use_container_width=True):
                bookmark_manager.clear_bookmarks()
                st.success("All bookmarks cleared!")
                st.rerun()
        
        st.divider()
        
        # Display bookmarks
        for bookmark in bookmarks:
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.subheader(bookmark['title'])
                    st.caption(f"📡 {bookmark['feed_name']} • Bookmarked: {bookmark['bookmarked_at'][:19]}")
                    
                    if bookmark['summary']:
                        st.write(bookmark['summary'][:300] + "..." if len(bookmark['summary']) > 300 else bookmark['summary'])
                    
                    if bookmark['link']:
                        st.link_button("🔗 Read Full Article", bookmark['link'])
                
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_bookmark_{bookmark['link']}"):
                        bookmark_manager.remove_bookmark(bookmark['link'])
                        st.success("Bookmark removed!")
                        st.rerun()
            
            st.divider()

elif current_page == "summary":
    st.markdown(f'<h1>{svg_icon_html("summary", 32)} Combined Summary</h1>', unsafe_allow_html=True)
    
    bookmarks = bookmark_manager.get_bookmarks()
    
    if not bookmarks:
        st.info("No bookmarked articles to summarize. Please bookmark some articles first!")
    else:
        st.write(f"Ready to summarize {len(bookmarks)} bookmarked articles")
        
        # Check if we have an existing summary
        if 'combined_summary' not in st.session_state:
            st.session_state.combined_summary = None
        
        # Generate summary button
        if st.button("🤖 Generate AI Summary", type="primary"):
            with st.spinner("Fetching full articles and generating summary..."):
                try:
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Fetch full article content for all bookmarks
                    full_articles = []
                    
                    for i, bookmark in enumerate(bookmarks):
                        status_text.text(f"Scraping article {i+1} of {len(bookmarks)}: {bookmark['title'][:50]}...")
                        try:
                            full_content = article_scraper.scrape_article(bookmark['link'])
                            if full_content:
                                full_articles.append({
                                    'title': bookmark['title'],
                                    'content': full_content,
                                    'source': bookmark['feed_name']
                                })
                        except Exception as e:
                            st.warning(f"Failed to scrape: {bookmark['title']}")
                        
                        progress_bar.progress((i + 1) / len(bookmarks))
                    
                    status_text.text("Generating AI summary...")
                    
                    if full_articles:
                        # Generate combined summary
                        combined_summary = ai_summarizer.create_combined_summary(full_articles)
                        
                        if combined_summary:
                            st.session_state.combined_summary = combined_summary
                            status_text.text("Summary generated successfully!")
                            progress_bar.progress(1.0)
                        else:
                            st.error("Failed to generate summary")
                    else:
                        st.error("No articles could be scraped for summarization")
                        
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
        
        # Display generated summary
        if st.session_state.combined_summary:
            st.success("Summary generated successfully!")
            
            st.markdown(f'<h3>{svg_icon_html("summary", 24)} Generated Summary</h3>', unsafe_allow_html=True)
            
            # Text display with copy functionality
            st.text_area(
                "Combined Summary", 
                st.session_state.combined_summary, 
                height=400,
                help="Use Ctrl+A to select all, then Ctrl+C to copy"
            )
            
            # Download as text
            st.download_button(
                label="📥 Download as Text",
                data=st.session_state.combined_summary,
                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            # Audio generation section
            st.markdown(f'<h3>{svg_icon_html("audio", 24)} Audio Options</h3>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎵 Generate Audio", use_container_width=True):
                    with st.spinner("Converting text to speech..."):
                        try:
                            audio_file = audio_processor.text_to_speech(st.session_state.combined_summary)
                            if audio_file:
                                st.session_state.audio_file = audio_file
                                st.success("Audio generated!")
                            else:
                                st.error("Failed to generate audio - please check your OpenAI API key quota")
                        except Exception as e:
                            error_msg = str(e)
                            if "quota" in error_msg.lower() or "429" in error_msg:
                                st.error("Your OpenAI API key has exceeded its quota. Please check your billing at https://platform.openai.com/account/billing")
                            else:
                                st.error(f"Error generating audio: {error_msg}")
            
            with col2:
                if 'audio_file' in st.session_state and st.session_state.audio_file:
                    st.audio(st.session_state.audio_file, format='audio/mp3')
            
            with col3:
                if 'audio_file' in st.session_state and st.session_state.audio_file:
                    try:
                        with open(st.session_state.audio_file, 'rb') as f:
                            audio_data = f.read()
                        st.download_button(
                            label="📥 Download MP3",
                            data=audio_data,
                            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error preparing download: {str(e)}")

elif current_page == "settings":
    st.markdown(f'<h1>{svg_icon_html("settings", 32)} Settings</h1>', unsafe_allow_html=True)
    
    # API Keys section
    st.markdown(f'<h3>{svg_icon_html("key", 24)} API Keys</h3>', unsafe_allow_html=True)
    st.caption("These keys are stored securely and persist across sessions")
    
    with st.expander("Configure API Keys", expanded=True):
        # Get current API keys from database
        current_gemini_key = db.get_setting("GEMINI_API_KEY", "")
        current_openai_key = db.get_setting("OPENAI_API_KEY", "")
        
        # Show/hide toggle for API keys
        show_keys = st.checkbox("Show API Keys", value=False)
        
        gemini_key = st.text_input(
            "Gemini API Key", 
            value=current_gemini_key if show_keys else ("*" * 20 if current_gemini_key else ""),
            type="default" if show_keys else "password",
            help="Get your API key from https://ai.google.dev"
        )
        
        openai_key = st.text_input(
            "OpenAI API Key", 
            value=current_openai_key if show_keys else ("*" * 20 if current_openai_key else ""),
            type="default" if show_keys else "password", 
            help="Get your API key from https://platform.openai.com"
        )
        
        if st.button("💾 Save API Keys", type="primary"):
            if gemini_key and not gemini_key.startswith("*"):
                db.save_setting("GEMINI_API_KEY", gemini_key)
                os.environ["GEMINI_API_KEY"] = gemini_key
            
            if openai_key and not openai_key.startswith("*"):
                db.save_setting("OPENAI_API_KEY", openai_key)
                os.environ["OPENAI_API_KEY"] = openai_key
            
            st.success("API keys saved successfully!")
            st.rerun()
    
    # App Settings section
    st.markdown(f'<h3>{svg_icon_html("settings", 24)} Application Settings</h3>', unsafe_allow_html=True)
    
    with st.expander("AI Settings", expanded=True):
        # AI service selection
        ai_services = ["gemini", "openai"]
        current_ai_service = db.get_setting("ai_service", "gemini")
        
        selected_ai_service = st.selectbox(
            "AI Summarization Service",
            ai_services,
            index=ai_services.index(current_ai_service) if current_ai_service in ai_services else 0,
            help="Choose between Gemini and OpenAI for article summarization"
        )
        
        if st.button("💾 Save AI Settings"):
            db.save_setting("ai_service", selected_ai_service)
            st.success("AI service settings saved! Restart may be needed for changes to take effect.")
    
    with st.expander("🔊 Audio Settings", expanded=True):
        # Voice selection for TTS
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        current_voice = db.get_setting("tts_voice", "alloy")
        
        selected_voice = st.selectbox(
            "Text-to-Speech Voice",
            voice_options,
            index=voice_options.index(current_voice) if current_voice and current_voice in voice_options else 0
        )
        
        # Speaking rate
        speaking_rate = st.slider(
            "Speaking Rate", 
            min_value=0.5, 
            max_value=2.0, 
            value=db.get_setting("speaking_rate", 1.0),
            step=0.1
        )
        
        if st.button("💾 Save Audio Settings"):
            db.save_setting("tts_voice", selected_voice)
            db.save_setting("speaking_rate", speaking_rate)
            st.success("Audio settings saved!")
    
    with st.expander("Feed Settings", expanded=True):
        # Auto-refresh interval
        refresh_intervals = {
            "Manual only": 0,
            "Every hour": 60,
            "Every 6 hours": 360,
            "Daily": 1440
        }
        
        current_interval = db.get_setting("auto_refresh_minutes", 0)
        current_label = next(
            (label for label, minutes in refresh_intervals.items() if minutes == current_interval),
            "Manual only"
        )
        
        refresh_interval = st.selectbox(
            "Auto-refresh RSS feeds",
            list(refresh_intervals.keys()),
            index=list(refresh_intervals.keys()).index(current_label)
        )
        
        # Articles to keep per feed
        articles_to_keep = st.number_input(
            "Articles to keep per feed",
            min_value=10,
            max_value=1000,
            value=db.get_setting("articles_per_feed", 100),
            step=10
        )
        
        if st.button("💾 Save Feed Settings"):
            db.save_setting("auto_refresh_minutes", refresh_intervals[refresh_interval])
            db.save_setting("articles_per_feed", articles_to_keep)
            st.success("Feed settings saved!")
    
    # Database management
    st.subheader("🗄️ Database Management")
    
    with st.expander("Database Actions"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Show Database Stats", use_container_width=True):
                stats = {
                    "RSS Feeds": len(rss_manager.get_feeds()),
                    "Total Articles": len(rss_manager.get_all_articles()),
                    "Bookmarks": bookmark_manager.get_bookmark_count(),
                    "Settings": len(db.get_all_settings())
                }
                
                for key, value in stats.items():
                    st.metric(key, value)
        
        with col2:
            st.warning("⚠️ Danger Zone")
            if st.button("🗑️ Clear All Data", use_container_width=True):
                if st.button("⚠️ Confirm Delete All", type="secondary"):
                    # This would need implementation
                    st.error("This feature is not yet implemented for safety")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("RSS Reader with AI • Powered by Streamlit")