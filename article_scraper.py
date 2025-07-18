import trafilatura
import requests
from typing import Optional

class ArticleScraper:
    def __init__(self):
        self.timeout = 30
    
    def scrape_article(self, url: str) -> Optional[str]:
        """
        Scrape the full text content from an article URL
        Returns clean, readable text content
        """
        try:
            print(f"Scraping full article from: {url}")
            
            # Use trafilatura to fetch and extract content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                print(f"Failed to download content from {url}")
                return None
            
            print(f"Downloaded {len(downloaded)} bytes from {url}")
            
            # Extract the main text content
            text = trafilatura.extract(downloaded)
            
            if text and len(text.strip()) > 100:  # Ensure we got meaningful content
                print(f"Extracted {len(text)} characters of article text from {url}")
                print(f"Article preview: {text[:200]}...")
                return text.strip()
            else:
                print(f"No meaningful content extracted from {url}")
                return None
                
        except Exception as e:
            print(f"Error scraping article from {url}: {str(e)}")
            return None
    
    def scrape_multiple_articles(self, urls: list) -> dict:
        """
        Scrape multiple articles and return a dictionary of url -> content
        """
        results = {}
        
        for url in urls:
            content = self.scrape_article(url)
            if content:
                results[url] = content
        
        return results
    
    def get_article_metadata(self, url: str) -> dict:
        """
        Extract metadata from an article using trafilatura
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return {}
            
            metadata = trafilatura.extract_metadata(downloaded)
            
            result = {}
            if metadata:
                result['title'] = getattr(metadata, 'title', '')
                result['author'] = getattr(metadata, 'author', '')
                result['date'] = getattr(metadata, 'date', '')
                result['description'] = getattr(metadata, 'description', '')
                result['sitename'] = getattr(metadata, 'sitename', '')
                result['url'] = getattr(metadata, 'url', url)
            
            return result
            
        except Exception as e:
            print(f"Error extracting metadata from {url}: {str(e)}")
            return {}
