import os
from google import genai
from google.genai import types
from typing import List, Dict, Optional

class AISummarizer:
    def __init__(self, db_manager=None):
        from database import DatabaseManager
        self.db = db_manager or DatabaseManager()
        
        # Get preferred AI service from settings
        self.ai_service = self.db.get_setting("ai_service", "gemini")
        
        # Initialize based on preferred service
        self.gemini_client = None
        self.openai_client = None
        
        if self.ai_service == "gemini":
            self._init_gemini()
        else:
            self._init_openai()
    
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
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            # Get API key from database first, then environment
            api_key = self.db.get_setting("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            if api_key:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=api_key)
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                self.model = "gpt-4o"
                print("OpenAI initialized for summarization")
            else:
                print("No OpenAI API key found")
        except Exception as e:
            print(f"Failed to initialize OpenAI: {str(e)}")
    
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

            {text}"""
            
            if self.ai_service == "gemini" and self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                response_text = response.text
            elif self.ai_service == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content
            else:
                print(f"No {self.ai_service} client available")
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
                
                # Log content preview to verify we have full article content
                content_preview = article['content'][:300].replace('\n', ' ')
                print(f"Content preview: {content_preview}...")
                
                summary = self.summarize_article(article['content'])
                if summary:
                    individual_summaries.append({
                        'title': article['title'],
                        'summary': summary,
                        'source': article['source']
                    })
                    print(f"Generated summary for: {article['title'][:50]}...")
            
            if not individual_summaries:
                return None
            
            # Create a combined summary from individual summaries
            combined_text = ""
            for summary_data in individual_summaries:
                combined_text += summary_data['summary'] + "\n\n"
            
            # Generate final combined summary
            final_prompt = f"""Please create a comprehensive but concise summary that combines the key information from these {len(individual_summaries)} articles. 

            CRITICAL FORMATTING REQUIREMENTS:
            - Write in clear, flowing paragraphs suitable for text-to-speech conversion
            - Use natural, conversational language as if explaining to a friend
            - NO asterisks, bullet points, dashes, or special formatting characters
            - NO article titles, source names, or references to "articles" or "reports"
            - NO section headers, numbered lists, or markdown formatting
            - NO quotes, hashtags, or technical jargon
            - Present information as continuous, readable prose with proper paragraph breaks
            - Organize content logically but without explicit section divisions
            - If there are different viewpoints, weave them naturally into the narrative

            Here is the content to summarize:
            {combined_text}"""
            
            if self.ai_service == "gemini" and self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model=self.model,
                    contents=final_prompt
                )
                response_text = response.text
            elif self.ai_service == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": final_prompt}]
                )
                response_text = response.choices[0].message.content
            else:
                print(f"No {self.ai_service} client available")
                return None
            
            # Clean up the response to ensure it meets our formatting requirements
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
            prompt = f"""Please summarize the following article with a focus on: {focus}
            
            Extract and highlight information that is most relevant to this focus area:

            {text}"""
            
            if self.ai_service == "gemini" and self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return response.text if response.text else None
            elif self.ai_service == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content if response.choices[0].message.content else None
            else:
                print(f"No {self.ai_service} client available")
                return None
            
        except Exception as e:
            print(f"Error summarizing with focus: {str(e)}")
            return None
    
    def _clean_summary_text(self, text: str) -> str:
        """
        Clean and sanitize summary text for optimal text-to-speech conversion
        """
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold **text**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Remove italic *text*
        text = re.sub(r'`([^`]+)`', r'\1', text)        # Remove code `text`
        
        # Remove bullet points and list markers
        text = re.sub(r'^\s*[-•*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove section headers (lines that are all caps or end with colons)
        text = re.sub(r'^\s*[A-Z\s]+:?\s*$', '', text, flags=re.MULTILINE)
        
        # Remove hashtags and social media references
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'@\w+', '', text)
        
        # Remove quotes and special characters
        text = re.sub(r'["""''`]', '', text)
        text = re.sub(r'[\[\]{}]', '', text)
        
        # Remove references to articles, reports, sources
        text = re.sub(r'\b(according to|the article|the report|sources say|reports indicate)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(article|report|source|study|research)\s+(states|shows|indicates|reveals|suggests)\b', '', text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces and line breaks
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up paragraph breaks
        
        # Remove extra whitespace
        text = text.strip()
        
        # Ensure proper sentence structure
        sentences = text.split('. ')
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Only keep substantial sentences
                if not sentence.endswith('.'):
                    sentence += '.'
                cleaned_sentences.append(sentence)
        
        # Join sentences and create proper paragraphs
        result = ' '.join(cleaned_sentences)
        
        # Add paragraph breaks for better readability (every 3-4 sentences)
        sentences = result.split('. ')
        paragraphs = []
        current_paragraph = []
        
        for i, sentence in enumerate(sentences):
            current_paragraph.append(sentence)
            if (i + 1) % 4 == 0 or i == len(sentences) - 1:  # Every 4 sentences or last sentence
                paragraph_text = '. '.join(current_paragraph)
                if not paragraph_text.endswith('.') and paragraph_text:
                    paragraph_text += '.'
                paragraphs.append(paragraph_text)
                current_paragraph = []
        
        return '\n\n'.join(paragraphs)
