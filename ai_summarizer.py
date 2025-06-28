import os
from google import genai
from google.genai import types
from typing import List, Dict, Optional

class AISummarizer:
    def __init__(self, db_manager=None):
        from database import DatabaseManager
        self.db = db_manager or DatabaseManager()
        
        # Use only Gemini for AI summarization
        self.gemini_client = None
        self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Gemini client"""
        try:
            # Get API key from database first, then environment
            api_key = self.db.get_setting("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key)
                # the newest Gemini model is "gemini-2.5-flash" 
                # do not change this unless explicitly requested by the user
                self.model = "gemini-2.5-flash"
                print("Gemini AI initialized for summarization")
            else:
                print("No Gemini API key found")
        except Exception as e:
            print(f"Failed to initialize Gemini: {str(e)}")
    
    def summarize_article(self, text: str) -> Optional[str]:
        """Summarize a single article"""
        try:
            prompt = f"""Please create a concise summary of the following article. 
            
            IMPORTANT FORMATTING REQUIREMENTS:
            - Write in clear, flowing paragraphs with natural line breaks
            - Use simple, conversational language suitable for text-to-speech
            - NO asterisks, bullet points, or special formatting characters
            - NO article titles or source names in the summary
            - NO hashtags, quotes, or markdown formatting
            - Focus on the key information as if you're telling someone about it in conversation
            - Use complete sentences and proper paragraph structure

            Article text:
            {text}"""
            
            # Generate summary using Gemini only
            if self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                response_text = response.text or ""
            else:
                print("No Gemini client available")
                return None
            
            # Clean up the response to ensure it meets our formatting requirements
            if response_text:
                cleaned_text = self._clean_summary_text(response_text)
                return cleaned_text
            else:
                return None
            
        except Exception as e:
            print(f"Error summarizing article: {str(e)}")
            return None
    
    def create_combined_summary(self, articles: List[Dict]) -> Optional[str]:
        """
        Create a combined summary from multiple articles
        articles should be a list of dicts with 'title', 'content', and 'source' keys
        """
        try:
            if not articles:
                return None
            
            # First, summarize each article individually
            individual_summaries = []
            for article in articles:
                content_length = len(article['content'])
                print(f"Processing article: {article['title'][:50]}... ({content_length} characters)")
                
                # Create content preview for debugging
                content_preview = article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
                print(f"Content preview: {content_preview}")
                
                summary = self.summarize_article(article['content'])
                if summary:
                    individual_summaries.append({
                        'title': article['title'],
                        'source': article.get('source', 'Unknown'),
                        'summary': summary
                    })
                    print(f"Generated summary for: {article['title'][:50]}...")
            
            if not individual_summaries:
                return None
            
            # Combine all summaries into one cohesive summary
            combined_prompt = """Create a cohesive summary from the following individual article summaries. 

            IMPORTANT FORMATTING REQUIREMENTS:
            - Write in clear, flowing paragraphs with natural line breaks
            - Use simple, conversational language suitable for text-to-speech
            - NO asterisks, bullet points, or special formatting characters
            - NO article titles or source names in the summary
            - NO hashtags, quotes, or markdown formatting
            - Focus on the key themes and information across all articles
            - Present information as if you're having a conversation about the news
            - Group related topics together naturally
            - Use complete sentences and proper paragraph structure

            Individual summaries to combine:
            """
            
            for i, summary_data in enumerate(individual_summaries, 1):
                combined_prompt += f"\n\nSummary {i}: {summary_data['summary']}"
            
            # Generate combined summary using Gemini only
            if self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=combined_prompt
                )
                response_text = response.text or ""
            else:
                print("No Gemini client available")
                return None
            
            if response_text:
                cleaned_text = self._clean_summary_text(response_text)
                return cleaned_text
            else:
                return None
            
        except Exception as e:
            print(f"Error creating combined summary: {str(e)}")
            return None
    
    def summarize_with_focus(self, text: str, focus: str) -> Optional[str]:
        """Summarize an article with a specific focus or angle"""
        try:
            prompt = f"""Please create a summary of the following article with a specific focus on: {focus}

            IMPORTANT FORMATTING REQUIREMENTS:
            - Write in clear, flowing paragraphs with natural line breaks
            - Use simple, conversational language suitable for text-to-speech
            - NO asterisks, bullet points, or special formatting characters
            - NO article titles or source names in the summary
            - NO hashtags, quotes, or markdown formatting
            - Focus specifically on aspects related to: {focus}
            - Present information as if you're explaining it in conversation
            - Use complete sentences and proper paragraph structure

            Article text:
            {text}"""
            
            # Generate focused summary using Gemini only
            if self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                response_text = response.text or ""
            else:
                print("No Gemini client available")
                return None
            
            if response_text:
                cleaned_text = self._clean_summary_text(response_text)
                return cleaned_text
            else:
                return None
            
        except Exception as e:
            print(f"Error creating focused summary: {str(e)}")
            return None
    
    def _clean_summary_text(self, text: str) -> str:
        """
        Clean and sanitize summary text for optimal text-to-speech conversion
        """
        if not text:
            return text
        
        # Remove markdown formatting
        text = text.replace('**', '').replace('*', '')
        text = text.replace('##', '').replace('#', '')
        text = text.replace('---', '')
        
        # Remove bullet points and list formatting
        text = text.replace('• ', '').replace('- ', '')
        text = text.replace('1. ', '').replace('2. ', '').replace('3. ', '')
        
        # Remove quotes and special characters that don't read well
        text = text.replace('"', '').replace('"', '').replace('"', '')
        text = text.replace(''', "'").replace(''', "'")
        
        # Clean up multiple spaces and line breaks
        text = ' '.join(text.split())
        
        # Add natural pauses for better TTS flow
        text = text.replace('. ', '. ')
        text = text.replace('? ', '? ')
        text = text.replace('! ', '! ')
        
        return text.strip()