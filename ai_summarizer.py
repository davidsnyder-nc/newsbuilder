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
                # Use the fastest Gemini model for speed optimization
                self.model = "gemini-1.5-flash"
                print("Gemini AI initialized for summarization")
            else:
                print("No Gemini API key found")
        except Exception as e:
            print(f"Failed to initialize Gemini: {str(e)}")
    
    def summarize_article(self, text: str) -> Optional[str]:
        """Summarize a single article"""
        try:
            prompt = f"""Create a clear, concise summary of this article using proper paragraph formatting:

            FORMATTING REQUIREMENTS:
            - Write 2-3 well-structured paragraphs with clear line breaks between them
            - Start each paragraph on a new line with proper spacing
            - Use conversational, easy-to-read language
            - NO bullet points, asterisks, or special formatting
            - NO article titles or source names
            - Focus on the main points and key details
            - Make it sound natural for reading aloud

            Article text:
            {text}"""
            
            # Generate summary using Gemini only
            if self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
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
            combined_prompt = """Create a comprehensive news summary by combining these individual article summaries:

            FORMATTING REQUIREMENTS:
            - Write 3-4 well-structured paragraphs with clear line breaks
            - Group related topics together naturally
            - Use conversational, natural language for audio playback
            - NO bullet points, asterisks, or special formatting
            - NO source names or article titles
            - Present as a flowing narrative about current events
            - Make smooth transitions between different topics

            Individual summaries to combine:
            """
            
            for i, summary_data in enumerate(individual_summaries, 1):
                combined_prompt += f"\n\nSummary {i}: {summary_data['summary']}"
            
            # Generate combined summary using Gemini only
            if self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
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
                    model="gemini-1.5-flash",
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
        
        # Preserve paragraph breaks but clean up excessive spacing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = ' '.join(line.split())  # Clean internal spacing
            if cleaned_line.strip():  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Rejoin with proper paragraph spacing
        text = '\n\n'.join(cleaned_lines)
        
        # Add natural pauses for better TTS flow
        text = text.replace('. ', '. ')
        text = text.replace('? ', '? ')
        text = text.replace('! ', '! ')
        
        return text.strip()