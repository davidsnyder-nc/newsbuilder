import os
import io
from google.cloud import texttospeech
from pydub import AudioSegment
from typing import Optional
import tempfile

class AudioProcessor:
    def __init__(self):
        # Initialize Google TTS client
        # Note: This requires GOOGLE_APPLICATION_CREDENTIALS environment variable
        # or proper authentication setup
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
            self.voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-J",  # A good quality neural voice
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
        except Exception as e:
            print(f"Warning: Google TTS client initialization failed: {str(e)}")
            self.tts_client = None
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech using Google TTS
        Returns the path to the generated audio file
        """
        if not self.tts_client:
            print("TTS client not available")
            return None
        
        try:
            # Create output path if not provided
            if not output_path:
                output_path = tempfile.mktemp(suffix=".mp3")
            
            # Check if text is too long for a single request
            max_chars = 5000  # Google TTS limit is around 5000 characters
            
            if len(text) <= max_chars:
                # Single request
                audio_content = self._synthesize_text(text)
                if audio_content:
                    with open(output_path, 'wb') as f:
                        f.write(audio_content)
                    return output_path
            else:
                # Split into chunks and combine
                return self._synthesize_long_text(text, output_path)
            
        except Exception as e:
            print(f"Error in text to speech: {str(e)}")
            return None
    
    def _synthesize_text(self, text: str) -> Optional[bytes]:
        """Synthesize a single chunk of text"""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"Error synthesizing text: {str(e)}")
            return None
    
    def _synthesize_long_text(self, text: str, output_path: str) -> Optional[str]:
        """
        Synthesize long text by splitting into chunks and combining audio files
        """
        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(text, 4500)  # Leave some buffer
            
            if not chunks:
                return None
            
            # Synthesize each chunk
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                audio_content = self._synthesize_text(chunk)
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
            print(f"Error synthesizing long text: {str(e)}")
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
