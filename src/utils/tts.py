import base64
from gtts import gTTS
from io import BytesIO
import streamlit as st
import logging
from pathlib import Path
from typing import Optional
import hashlib

class TextToSpeech:
    """
    Generates audio from text using gTTS and implements a persistent,
    file-based cache to avoid re-generating audio for the same text.
    """
    def __init__(self, cache_dir: str = ".cache/tts_cache"):
        """Initializes the TTS engine and ensures the cache directory exists."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_audio(self, text: str, lang: str = 'en') -> Optional[bytes]:
        """
        Generate audio bytes from text, using a reliable file-based cache.

        Args:
            text: The text to convert to speech.
            lang: The language of the text.

        Returns:
            The generated audio as bytes, or None if an error occurs.
        """
        try:
            # Use a deterministic hash for a stable cache key
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            cache_file = self.cache_dir / f"{text_hash}_{lang}.mp3"
            
            # Return cached audio if it exists
            if cache_file.exists():
                logging.info(f"TTS cache HIT for text: {text[:20]}...")
                return cache_file.read_bytes()
                
            # If not cached, generate new audio
            logging.info(f"TTS cache MISS for text: {text[:20]}.... Generating new audio.")
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_bytes = audio_fp.getvalue()
            
            # Cache the newly generated audio file
            cache_file.write_bytes(audio_bytes)
            
            return audio_bytes
        except Exception as e:
            logging.error(f"TTS generation failed: {str(e)}")
            st.warning(f"Could not generate audio for the text due to an error: {e}")
            return None

def autoplay_audio(text: str) -> None:
    """
    Streamlit function to generate and display an audio player in the browser.

    Args:
        text: The text to be spoken.
    """
    try:
        tts = TextToSpeech()
        audio_bytes = tts.generate_audio(text)
        
        if audio_bytes:
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            # --- UPDATED AUDIO TAG ---
            # Added the 'controls' attribute to make the player visible.
            # This provides play, pause (stop), and volume controls.
            audio_tag = f"""
                <audio controls>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Your browser does not support the audio element.
                </audio>
            """
            # Removed height=0 to ensure the controls are visible
            st.components.v1.html(audio_tag)
    except Exception as e:
        st.error(f"Audio playback failed: {str(e)}")
        logging.error(f"Audio playback error: {str(e)}", exc_info=True)
