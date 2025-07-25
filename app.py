import streamlit as st
import os
from datetime import datetime
from rss_manager import RSSManager
from bookmark_manager import BookmarkManager
from article_scraper import ArticleScraper
from ai_summarizer import AISummarizer
from audio_processor import AudioProcessor
from database import DatabaseManager


# Configure page
st.set_page_config(
    page_title="RSS Reader with AI Summarization",

    layout="wide",
    initial_sidebar_state="expanded"
)

# Material Design CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    .stApp {
        font-family: 'Roboto', sans-serif;
        background-color: #fafafa;
    }
    
    /* Container styling for articles */
    .stContainer {
        background: white;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Material Design Typography */
    .md-headline {
        font-size: 24px;
        font-weight: 400;
        margin: 16px 0;
        color: #212121;
    }
    
    .md-title {
        font-size: 20px;
        font-weight: 500;
        margin: 12px 0 8px 0;
        color: #212121;
    }
    
    .md-subtitle {
        font-size: 16px;
        font-weight: 400;
        color: #757575;
        margin: 8px 0;
    }
    
    .md-body {
        font-size: 14px;
        font-weight: 400;
        line-height: 1.5;
        color: #424242;
    }
    
    .md-caption {
        font-size: 12px;
        font-weight: 400;
        color: #757575;
    }
    
    /* Material Design Buttons */
    .stButton > button {
        background-color: #1976d2;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.25);
    }
    
    /* Clean interface - remove icons and extra spacing */
    .stSelectbox > div > div {
        border-radius: 4px;
    }
    
    .stTextInput > div > div {
        border-radius: 4px;
    }
    
    /* Material spacing */
    .mb-2 { margin-bottom: 16px; }
    .mt-2 { margin-top: 16px; }
    .p-2 { padding: 16px; }
    
    /* Clean sidebar */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

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
st.sidebar.markdown('<h1 class="md-headline">RSS Reader</h1>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation menu
pages = {
    "Read Articles": "articles",
    "RSS Feeds": "feeds", 
    "Bookmarks": "bookmarks",
    "Summary": "summary",
    "Settings": "settings"
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
st.sidebar.markdown('<h3 class="md-title">Quick Stats</h3>', unsafe_allow_html=True)

feeds_count = len(rss_manager.get_feeds())
bookmarks_count = bookmark_manager.get_bookmark_count()

st.sidebar.metric("RSS Feeds", feeds_count)
st.sidebar.metric("Bookmarks", bookmarks_count)

if feeds_count > 0:
    if st.sidebar.button("Refresh All Feeds", use_container_width=True):
        with st.spinner("Refreshing feeds..."):
            rss_manager.refresh_all_feeds()
        st.success("Feeds refreshed!")
        st.rerun()

# Page content
if current_page == "articles":
    st.markdown('<h1 class="md-headline">RSS Articles</h1>', unsafe_allow_html=True)
    
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
                    # Check if article has an image
                    if article.get('image_url'):
                        col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
                        
                        with col1:
                            try:
                                st.image(article['image_url'], width=120)
                            except:
                                pass  # Skip if image fails to load
                        
                        with col2:
                            st.markdown(f"**{article['title']}**")
                            st.caption(f"{article['feed_name']} • {article.get('published', 'No date')}")
                            
                            if article['summary']:
                                summary_text = article['summary'][:120] + "..." if len(article['summary']) > 120 else article['summary']
                                st.markdown(f"<small>{summary_text}</small>", unsafe_allow_html=True)
                        
                        with col3:
                            if article['link']:
                                st.link_button("Read", article['link'], help="Read Full Article")
                        
                        with col4:
                            is_bookmarked = bookmark_manager.is_bookmarked(article['link'])
                            
                            if is_bookmarked:
                                if st.button("✓", key=f"bookmark_img_{article['link']}", disabled=True, help="Bookmarked"):
                                    pass
                            else:
                                if st.button("Save", key=f"bookmark_img_{article['link']}", help="Bookmark"):
                                    if bookmark_manager.add_bookmark(article):
                                        st.success("Bookmarked!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to bookmark")
                    else:
                        col1, col2, col3 = st.columns([5, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{article['title']}**")
                            st.caption(f"{article['feed_name']} • {article.get('published', 'No date')}")
                            
                            if article['summary']:
                                summary_text = article['summary'][:150] + "..." if len(article['summary']) > 150 else article['summary']
                                st.markdown(f"<small>{summary_text}</small>", unsafe_allow_html=True)
                        
                        with col2:
                            if article['link']:
                                st.link_button("Read", article['link'], help="Read Full Article")
                        
                        with col3:
                            is_bookmarked = bookmark_manager.is_bookmarked(article['link'])
                            
                            if is_bookmarked:
                                if st.button("✓", key=f"bookmark_txt_{article['link']}", disabled=True, help="Bookmarked"):
                                    pass
                            else:
                                if st.button("Save", key=f"bookmark_txt_{article['link']}", help="Bookmark"):
                                    if bookmark_manager.add_bookmark(article):
                                        st.success("Bookmarked!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to bookmark")
                
                    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

elif current_page == "feeds":
    st.markdown('<h1 class="md-headline">RSS Feed Management</h1>', unsafe_allow_html=True)
    
    # Add new feed section
    with st.expander("Add New RSS Feed", expanded=True):
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
    st.markdown(f'<h3> Current RSS Feeds</h3>', unsafe_allow_html=True)
    
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
                    if st.button("Delete", key=f"delete_{feed['name']}", help="Delete feed"):
                        rss_manager.remove_feed(feed['name'])
                        st.success(f"Deleted feed: {feed['name']}")
                        st.rerun()
            
            st.divider()

elif current_page == "bookmarks":
    st.markdown(f'<h1> Bookmarked Articles</h1>', unsafe_allow_html=True)
    
    bookmarks = bookmark_manager.get_bookmarks()
    
    if not bookmarks:
        st.info("No bookmarked articles yet. Bookmark some articles from the RSS feeds to see them here!")
    else:
        # Actions section
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Generate Combined Summary", type="primary", use_container_width=True):
                st.query_params["page"] = "summary"
                st.rerun()
        with col2:
            if st.button("Clear All Bookmarks", use_container_width=True):
                bookmark_manager.clear_bookmarks()
                st.success("All bookmarks cleared!")
                st.rerun()
        
        st.divider()
        
        # Display bookmarks
        for bookmark in bookmarks:
            with st.container():
                # Check if bookmark has an image
                if bookmark.get('image_url'):
                    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
                    
                    with col1:
                        try:
                            st.image(bookmark['image_url'], width=120)
                        except:
                            pass  # Skip if image fails to load
                    
                    with col2:
                        st.markdown(f"**{bookmark['title']}**")
                        st.caption(f"{bookmark['feed_name']} • Bookmarked: {bookmark['bookmarked_at'][:16]}")
                        
                        if bookmark['summary']:
                            summary_text = bookmark['summary'][:120] + "..." if len(bookmark['summary']) > 120 else bookmark['summary']
                            st.markdown(f"<small>{summary_text}</small>", unsafe_allow_html=True)
                    
                    with col3:
                        if bookmark['link']:
                            st.link_button("Read", bookmark['link'], help="Read Full Article")
                    
                    with col4:
                        if st.button("Remove", key=f"remove_bookmark_{bookmark['link']}", help="Remove Bookmark"):
                            bookmark_manager.remove_bookmark(bookmark['link'])
                            st.success("Removed!")
                            st.rerun()
                else:
                    col1, col2, col3 = st.columns([5, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{bookmark['title']}**")
                        st.caption(f"{bookmark['feed_name']} • Bookmarked: {bookmark['bookmarked_at'][:16]}")
                        
                        if bookmark['summary']:
                            summary_text = bookmark['summary'][:150] + "..." if len(bookmark['summary']) > 150 else bookmark['summary']
                            st.markdown(f"<small>{summary_text}</small>", unsafe_allow_html=True)
                    
                    with col2:
                        if bookmark['link']:
                            st.link_button("Read", bookmark['link'], help="Read Full Article")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_bookmark_{bookmark['link']}", help="Remove Bookmark"):
                            bookmark_manager.remove_bookmark(bookmark['link'])
                            st.success("Removed!")
                            st.rerun()
            
            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

elif current_page == "summary":
    st.markdown(f'<h1> Combined Summary</h1>', unsafe_allow_html=True)
    
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
            
            st.markdown(f'<h3> Generated Summary</h3>', unsafe_allow_html=True)
            
            # Text display with copy functionality
            st.text_area(
                "Combined Summary", 
                st.session_state.combined_summary, 
                height=400,
                help="Use Ctrl+A to select all, then Ctrl+C to copy"
            )
            
            # Text options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download as Text",
                    data=st.session_state.combined_summary,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                if st.button("Copy to Clipboard", use_container_width=True):
                    st.success("Use Ctrl+A and Ctrl+C in the text area above to copy!")
            
            # Audio generation section
            st.markdown('<h3 class="md-title">Audio Options</h3>', unsafe_allow_html=True)
            
            # Initialize audio generation state
            if 'audio_generating' not in st.session_state:
                st.session_state.audio_generating = False
            
            # Audio generation button
            if not st.session_state.audio_generating:
                if st.button("Generate Audio", use_container_width=True):
                    st.session_state.audio_generating = True
                    st.rerun()
            
            # Show spinner and generate audio
            if st.session_state.audio_generating:
                with st.spinner("Converting text to speech..."):
                    try:
                        audio_file = audio_processor.text_to_speech(st.session_state.combined_summary)
                        if audio_file:
                            st.session_state.audio_file = audio_file
                            st.session_state.audio_generating = False
                            st.success("Audio generated!")
                            st.rerun()
                        else:
                            st.session_state.audio_generating = False
                            st.error("Failed to generate audio - please check your Gemini API key and Google Cloud TTS setup.")
                    except Exception as e:
                        st.session_state.audio_generating = False
                        error_msg = str(e)
                        if "quota" in error_msg.lower() or "429" in error_msg:
                            st.error("Your Google Cloud TTS quota has been exceeded. Please check your Google Cloud billing.")
                        else:
                            st.error(f"Error generating audio: {error_msg}")
            
            # Audio playback and download (only show if audio exists)
            if 'audio_file' in st.session_state and st.session_state.audio_file and not st.session_state.audio_generating:
                st.audio(st.session_state.audio_file, format='audio/mp3')
                
                try:
                    with open(st.session_state.audio_file, 'rb') as f:
                        audio_data = f.read()
                    st.download_button(
                        label="Download MP3",
                        data=audio_data,
                        file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error preparing download: {str(e)}")

elif current_page == "settings":
    st.markdown(f'<h1> Settings</h1>', unsafe_allow_html=True)
    
    # API Keys section
    st.markdown(f'<h3> API Keys</h3>', unsafe_allow_html=True)
    st.caption("These keys are stored securely and persist across sessions")
    
    with st.expander("Configure API Keys", expanded=True):
        # Get current Gemini API key from database
        current_gemini_key = db.get_setting("GEMINI_API_KEY", "")
        
        # Show/hide toggle for API key
        show_key = st.checkbox("Show API Key", value=False)
        
        gemini_key = st.text_input(
            "Gemini API Key", 
            value=current_gemini_key if show_key else ("*" * 20 if current_gemini_key else ""),
            type="default" if show_key else "password",
            help="Get your API key from https://ai.google.dev - Used for both AI summarization and text-to-speech"
        )
        
        if st.button("💾 Save API Key", type="primary"):
            if gemini_key and not gemini_key.startswith("*"):
                db.save_setting("GEMINI_API_KEY", gemini_key)
                os.environ["GEMINI_API_KEY"] = gemini_key
                st.success("Gemini API key saved successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid API key")
    
    # App Settings section
    st.markdown(f'<h3> Application Settings</h3>', unsafe_allow_html=True)
    
    with st.expander("🔊 Audio Settings", expanded=True):
        # Google TTS Voice selection - Neural2 and Studio voices
        voice_options = [
            # Premium Studio voices (highest quality)
            ("en-US-Studio-M", "Studio-M (Male) - Premium"),
            ("en-US-Studio-O", "Studio-O (Female) - Premium"),
            ("en-US-Studio-Q", "Studio-Q (Male) - Premium"),
            
            # Neural2 voices (high quality)
            ("en-US-Neural2-A", "Neural2-A (Female)"),
            ("en-US-Neural2-C", "Neural2-C (Female)"),
            ("en-US-Neural2-D", "Neural2-D (Male)"),
            ("en-US-Neural2-F", "Neural2-F (Female)"),
            ("en-US-Neural2-G", "Neural2-G (Female)"),
            ("en-US-Neural2-H", "Neural2-H (Female)"),
            ("en-US-Neural2-I", "Neural2-I (Male)"),
            ("en-US-Neural2-J", "Neural2-J (Male)"),
            
            # Standard voices
            ("en-US-Standard-A", "Standard-A (Female)"),
            ("en-US-Standard-B", "Standard-B (Male)"),
            ("en-US-Standard-C", "Standard-C (Female)"),
            ("en-US-Standard-D", "Standard-D (Male)"),
            ("en-US-Standard-E", "Standard-E (Female)"),
            ("en-US-Standard-F", "Standard-F (Female)"),
            ("en-US-Standard-G", "Standard-G (Female)"),
            ("en-US-Standard-H", "Standard-H (Female)"),
            ("en-US-Standard-I", "Standard-I (Male)"),
            ("en-US-Standard-J", "Standard-J (Male)")
        ]
        current_voice = db.get_setting("tts_voice", "en-US-Studio-O")
        
        voice_labels = [label for _, label in voice_options]
        voice_values = [value for value, _ in voice_options]
        
        current_index = voice_values.index(current_voice) if current_voice in voice_values else 0
        
        selected_voice_label = st.selectbox(
            "Google Text-to-Speech Voice",
            voice_labels,
            index=current_index,
            help="Studio voices offer premium quality with natural expressions. Neural2 voices provide high-quality synthesis. Standard voices are reliable basic options."
        )
        
        selected_voice = voice_values[voice_labels.index(selected_voice_label)]
        
        # Speaking rate
        speaking_rate = st.slider(
            "Speaking Rate", 
            min_value=0.5, 
            max_value=2.0, 
            value=db.get_setting("speaking_rate", 1.0),
            step=0.1,
            help="Adjust the speed of the generated speech"
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
            st.warning("Danger Zone")
            if st.button("Clear All Data", use_container_width=True):
                if st.button("Confirm Delete All", type="secondary"):
                    # This would need implementation
                    st.error("This feature is not yet implemented for safety")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("RSS Reader with AI • Powered by Streamlit")