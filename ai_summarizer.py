import os
from google import genai
from google.genai import types
from typing import List, Dict, Optional

class AISummarizer:
    def __init__(self):
        # Get API key from environment variables with fallback
        api_key = os.getenv("GEMINI_API_KEY", "default_key")
        self.client = genai.Client(api_key=api_key)
        # the newest Gemini model is "gemini-2.5-flash" 
        # do not change this unless explicitly requested by the user
        self.model = "gemini-2.5-flash"
    
    def summarize_article(self, text: str) -> Optional[str]:
        """Summarize a single article"""
        try:
            prompt = f"""Please create a concise summary of the following article. 
            Focus on the key points, main arguments, and important facts. 
            Keep the summary informative but readable:

            {text}"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else None
            
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
                summary = self.summarize_article(article['content'])
                if summary:
                    individual_summaries.append({
                        'title': article['title'],
                        'summary': summary,
                        'source': article['source']
                    })
            
            if not individual_summaries:
                return None
            
            # Create a combined summary from individual summaries
            combined_text = ""
            for i, summary_data in enumerate(individual_summaries, 1):
                combined_text += f"\n\n{i}. {summary_data['title']} (Source: {summary_data['source']})\n"
                combined_text += summary_data['summary']
            
            # Generate final combined summary
            final_prompt = f"""Please create a comprehensive but concise summary that combines the key information from these {len(individual_summaries)} articles. 
            
            Organize the content logically, identify common themes, and present the most important information in a clear, readable format. 
            
            If there are conflicting viewpoints, please mention them. Structure the summary with clear sections if appropriate:

            {combined_text}"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=final_prompt
            )
            
            return response.text if response.text else None
            
        except Exception as e:
            print(f"Error creating combined summary: {str(e)}")
            return None
    
    def summarize_with_focus(self, text: str, focus: str) -> Optional[str]:
        """Summarize an article with a specific focus or angle"""
        try:
            prompt = f"""Please summarize the following article with a focus on: {focus}
            
            Extract and highlight information that is most relevant to this focus area:

            {text}"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else None
            
        except Exception as e:
            print(f"Error summarizing with focus: {str(e)}")
            return None
