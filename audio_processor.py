import os
import io
import tempfile
import requests
import json
from typing import Optional
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self, db_manager=None):
        from database import DatabaseManager
        self.db = db_manager or DatabaseManager()
        
        # Initialize Google Cloud TTS using REST API with API key
        self.api_key = None
        self.tts_method = None
        
        # Get Gemini API key for Google Cloud TTS
        gemini_key = self.db.get_setting("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.api_key = gemini_key
            self.tts_method = "google"
            print("Google Cloud TTS initialized using REST API with Gemini API key")
        else:
            print("No Gemini API key found - cannot initialize Google TTS")
        
        if not self.tts_method:
            print("No TTS service available - please configure Gemini API key in Settings")
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech using Google Cloud TTS REST API
        Returns the path to the generated audio file
        """
        if not self.tts_method or not self.api_key:
            print("Google Cloud TTS not available")
            return None
        
        try:
            # Create output path if not provided
            if not output_path:
                output_path = tempfile.mktemp(suffix=".mp3")
            
            return self._google_text_to_speech(text, output_path)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error in Google TTS: {error_msg}")
            return None
    
    def _google_text_to_speech(self, text: str, output_path: str) -> Optional[str]:
        """Convert text to speech using Google Cloud TTS REST API"""
        try:
            # Check if text is too long for a single request
            max_chars = 5000  # Google TTS limit
            
            if len(text) <= max_chars:
                # Single request
                audio_content = self._google_synthesize_text(text)
                if audio_content:
                    with open(output_path, 'wb') as f:
                        f.write(audio_content)
                    return output_path
            else:
                # Split into chunks and combine
                return self._google_synthesize_long_text(text, output_path)
            
        except Exception as e:
            print(f"Error with Google TTS: {str(e)}")
            return None
    
    def _google_synthesize_text(self, text: str) -> Optional[bytes]:
        """Synthesize a single chunk of text using Google TTS REST API"""
        try:
            # Get voice settings from database
            voice_name = self.db.get_setting("tts_voice", "en-US-Neural2-J")
            speaking_rate = self.db.get_setting("speaking_rate", 1.0)
            
            # Google Cloud TTS REST API endpoint
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.api_key}"
            
            # Request payload
            payload = {
                "input": {
                    "text": text
                },
                "voice": {
                    "languageCode": "en-US",
                    "name": voice_name,
                    "ssmlGender": "NEUTRAL"
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": float(speaking_rate),
                    "pitch": 0.0
                }
            }
            
            # Make the request
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if "audioContent" in result:
                    # Decode base64 audio content
                    import base64
                    audio_content = base64.b64decode(result["audioContent"])
                    return audio_content
                else:
                    print("No audio content in response")
                    return None
            else:
                print(f"TTS API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            print(f"Error synthesizing text chunk: {str(e)}")
            return None
    
    def _google_synthesize_long_text(self, text: str, output_path: str) -> Optional[str]:
        """
        Synthesize long text using Google TTS by splitting into chunks and combining audio files
        """
        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(text, 4500)  # Leave some buffer
            
            if not chunks:
                return None
            
            # Synthesize each chunk
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                try:
                    audio_content = self._google_synthesize_text(chunk)
                    if audio_content:
                        # Convert to AudioSegment
                        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_content))
                        audio_segments.append(audio_segment)
                    else:
                        print(f"Failed to synthesize chunk {i+1}")
                except Exception as e:
                    print(f"Failed to synthesize chunk {i+1}: {str(e)}")
            
            if not audio_segments:
                return None
            
            # Combine all audio segments
            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                combined_audio += segment
            
            # Export to file
            combined_audio.export(output_path, format="mp3")
            return output_path
            
        except Exception as e:
            print(f"Error combining audio chunks: {str(e)}")
            return None
    
    def _split_text_into_chunks(self, text: str, max_chars: int) -> list:
        """
        Split text into chunks at sentence boundaries
        """
        if len(text) <= max_chars:
            return [text]
        
        # Split by sentences first
        sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the limit
            if len(current_chunk) + len(sentence) > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Single sentence is too long, split by words
                    words = sentence.split()
                    word_chunk = ""
                    for word in words:
                        if len(word_chunk) + len(word) + 1 > max_chars:
                            if word_chunk:
                                chunks.append(word_chunk.strip())
                                word_chunk = word
                            else:
                                # Single word is too long, just add it
                                chunks.append(word)
                        else:
                            word_chunk += " " + word if word_chunk else word
                    if word_chunk:
                        current_chunk = word_chunk
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get the duration of an audio file in seconds"""
        try:
            audio = AudioSegment.from_mp3(audio_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            print(f"Error getting audio duration: {str(e)}")
            return None