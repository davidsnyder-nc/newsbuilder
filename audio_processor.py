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

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AudioProcessor:
    def __init__(self):
        # Initialize TTS with fallback options
        self.google_tts_client = None
        self.openai_client = None
        self.tts_method = None
        
        # Try OpenAI TTS first (more reliable in this environment)
        if OPENAI_AVAILABLE:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.tts_method = "openai"
                    print("OpenAI TTS initialized successfully")
            except Exception as e:
                print(f"OpenAI TTS initialization failed: {str(e)}")
        
        # Fallback to Google Cloud TTS if OpenAI not available
        if not self.tts_method and GOOGLE_TTS_AVAILABLE:
            try:
                self.google_tts_client = texttospeech.TextToSpeechClient()
                self.voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Neural2-J",
                    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                )
                self.audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0
                )
                self.tts_method = "google"
                print("Google Cloud TTS initialized successfully")
            except Exception as e:
                print(f"Google Cloud TTS initialization failed: {str(e)}")
        
        if not self.tts_method:
            print("No TTS service available")
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech using available TTS service
        Returns the path to the generated audio file
        """
        if not self.tts_method:
            print("No TTS service available")
            return None
        
        try:
            # Create output path if not provided
            if not output_path:
                output_path = tempfile.mktemp(suffix=".mp3")
            
            if self.tts_method == "openai":
                return self._openai_text_to_speech(text, output_path)
            elif self.tts_method == "google":
                return self._google_text_to_speech(text, output_path)
            
        except Exception as e:
            print(f"Error in text to speech: {str(e)}")
            return None
    
    def _openai_text_to_speech(self, text: str, output_path: str) -> Optional[str]:
        """Convert text to speech using OpenAI TTS"""
        try:
            # Check if text is too long for a single request
            max_chars = 4096  # OpenAI TTS limit
            
            if len(text) <= max_chars:
                # Single request
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text,
                    response_format="mp3"
                )
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                # Split into chunks and combine
                return self._openai_synthesize_long_text(text, output_path)
            
        except Exception as e:
            print(f"Error with OpenAI TTS: {str(e)}")
            return None
    
    def _openai_synthesize_long_text(self, text: str, output_path: str) -> Optional[str]:
        """Synthesize long text using OpenAI TTS by splitting into chunks"""
        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(text, 4000)  # Leave some buffer
            
            if not chunks:
                return None
            
            # Synthesize each chunk
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                try:
                    response = self.openai_client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=chunk,
                        response_format="mp3"
                    )
                    
                    # Convert to AudioSegment
                    audio_segment = AudioSegment.from_mp3(io.BytesIO(response.content))
                    audio_segments.append(audio_segment)
                except Exception as e:
                    print(f"Failed to synthesize chunk {i+1}: {str(e)}")
            
            if not audio_segments:
                return None
            
            # Combine all audio segments
            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                # Add a small pause between segments
                pause = AudioSegment.silent(duration=500)  # 500ms pause
                combined_audio = combined_audio + pause + segment
            
            # Export combined audio
            combined_audio.export(output_path, format="mp3")
            return output_path
            
        except Exception as e:
            print(f"Error synthesizing long text with OpenAI: {str(e)}")
            return None
    
    def _google_text_to_speech(self, text: str, output_path: str) -> Optional[str]:
        """Convert text to speech using Google Cloud TTS"""
        try:
            # Check if text is too long for a single request
            max_chars = 5000  # Google TTS limit is around 5000 characters
            
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
            if not GOOGLE_TTS_AVAILABLE:
                return None
                
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.google_tts_client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"Error synthesizing text: {str(e)}")
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
                audio_content = self._google_synthesize_text(chunk)
                if audio_content:
                    # Convert to AudioSegment
                    audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_content))
                    audio_segments.append(audio_segment)
                else:
                    print(f"Failed to synthesize chunk {i+1}")
            
            if not audio_segments:
                return None
            
            # Combine all audio segments
            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                # Add a small pause between segments
                pause = AudioSegment.silent(duration=500)  # 500ms pause
                combined_audio = combined_audio + pause + segment
            
            # Export combined audio
            combined_audio.export(output_path, format="mp3")
            return output_path
            
        except Exception as e:
            print(f"Error synthesizing long text with Google: {str(e)}")
            return None
    
    def _split_text_into_chunks(self, text: str, max_chars: int) -> list:
        """
        Split text into chunks at sentence boundaries
        """
        import re
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed the limit
            if len(current_chunk) + len(sentence) + 2 > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
                else:
                    # Single sentence is too long, split it by words
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= max_chars:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    if temp_chunk:
                        current_chunk = temp_chunk
            else:
                current_chunk += sentence + ". "
        
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
