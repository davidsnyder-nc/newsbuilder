import os
import io
import tempfile
import requests
from typing import Optional
from pydub import AudioSegment

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False


class AudioProcessor:
    def __init__(self, db_manager=None):
        from database import DatabaseManager
        self.db = db_manager or DatabaseManager()
        
        # Initialize Google Cloud TTS only
        self.google_tts_client = None
        self.tts_method = None
        
        if GOOGLE_TTS_AVAILABLE:
            try:
                # Use Gemini API key for Google Cloud TTS authentication
                gemini_key = self.db.get_setting("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
                if gemini_key:
                    # Set the API key as environment variable for Google Cloud
                    os.environ["GOOGLE_API_KEY"] = gemini_key
                    
                    # Initialize Google Cloud TTS client
                    self.google_tts_client = texttospeech.TextToSpeechClient()
                    
                    # Get voice settings from database
                    voice_name = self.db.get_setting("tts_voice", "en-US-Neural2-J")
                    speaking_rate = self.db.get_setting("speaking_rate", 1.0)
                    
                    self.voice = texttospeech.VoiceSelectionParams(
                        language_code="en-US",
                        name=voice_name,
                        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                    )
                    self.audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=float(speaking_rate),
                        pitch=0.0
                    )
                    self.tts_method = "google"
                    print("Google Cloud TTS initialized using Gemini API key")
                else:
                    print("Gemini API key not found - cannot initialize Google TTS")
            except Exception as e:
                print(f"Google Cloud TTS initialization failed: {str(e)}")
        else:
            print("Google Cloud TTS library not available")
        
        if not self.tts_method:
            print("No TTS service available - please configure Gemini API key in Settings")
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech using Google Cloud TTS
        Returns the path to the generated audio file
        """
        if not self.tts_method or self.tts_method != "google":
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
        """Convert text to speech using Google Cloud TTS"""
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
        """Synthesize a single chunk of text using Google TTS"""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.google_tts_client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            return response.audio_content
            
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