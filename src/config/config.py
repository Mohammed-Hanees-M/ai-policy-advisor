import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

class GeminiConfig:
    """
    Centralized configuration for the Google Gemini API.
    """
    API_KEY: Optional[str] = None
    MODEL_NAME: str = "gemini-1.5-flash-latest"
    
    SAFETY_SETTINGS: List[Dict[str, str]] = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    GENERATION_CONFIG: Dict[str, Any] = {
        "temperature": 0.5,  # Increased slightly for more natural, conversational responses
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
        # --- THE FIX ---
        # Changed the default response type to plain text for natural chat.
        "response_mime_type": "text/plain"
    }

    @classmethod
    def initialize(cls) -> None:
        """Loads the API key and configures the Gemini client."""
        try:
            load_dotenv(override=True)
            cls.API_KEY = os.getenv("GEMINI_API_KEY")
            if not cls.API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables or .env file.")
            
            genai.configure(api_key=cls.API_KEY)
            logging.info(f"Gemini client configured successfully for model: {cls.MODEL_NAME}")
        except Exception as e:
            logging.critical(f"Gemini configuration failed: {e}")
            raise

class AppConfig:
    """
    Configuration for the Streamlit application settings.
    """
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "pptx", "png", "jpg", "jpeg"]

# --- Initialize all configurations on startup ---
try:
    GeminiConfig.initialize()
    logging.info("Application configuration loaded successfully.")
except Exception as e:
    # This will stop the app if the configuration fails, e.g., no API key
    raise RuntimeError(f"Fatal error during application startup: {e}")
