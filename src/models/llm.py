from src.config.config import GeminiConfig
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

class GeminiClient:
    def __init__(self):
        """Initialize the Gemini client with proper configuration"""
        try:
            self.model = genai.GenerativeModel(
                model_name=GeminiConfig.MODEL_NAME,
                safety_settings=GeminiConfig.SAFETY_SETTINGS
            )
            logging.info(f"Gemini client initialized with model: {GeminiConfig.MODEL_NAME}")
        except Exception as e:
            logging.critical(f"Failed to initialize Gemini client: {e}")
            raise

    def generate(
        self,
        prompt: str,
        history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generates a response using the provided history and context."""
        try:
            start_time = datetime.now()
            
            generation_config = context.get("generation_config", GeminiConfig.GENERATION_CONFIG)
            chat_session = self.model.start_chat(history=history)
            full_prompt = self._build_full_prompt(prompt, context)
            
            response = chat_session.send_message(
                content=full_prompt,
                generation_config=generation_config
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            logging.info(f"Generated response in {duration:.2f}s")
            
            return response.text
            
        except Exception as e:
            error_msg = f"Generation failed: {e}"
            logging.error(error_msg, exc_info=True)
            return f"⚠️ Error: {error_msg}"

    def _build_full_prompt(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Constructs the complete prompt with all necessary instructions.
        """
        prompt_parts = []
        
        # Add persona, mode, and the new response mode instructions
        if persona_prompt := context.get("persona_prompt"):
            prompt_parts.append(f"Your persona: {persona_prompt}")
        if mode_instruction := context.get("mode_instruction"):
            prompt_parts.append(f"Your current task mode: {mode_instruction}")
        # --- THE FIX ---
        # Add the new instruction for response length.
        if response_mode_instruction := context.get("response_mode_instruction"):
            prompt_parts.append(f"Your response style: {response_mode_instruction}")

        if retrieved_context := context.get("retrieved_context"):
            prompt_parts.append(
                "Please answer the user's query. Prioritize information from the context provided below. "
                "If the context does not contain the answer, use your general knowledge.\n"
                f"--- START OF CONTEXT ---\n{retrieved_context}\n--- END OF CONTEXT ---"
            )
        
        prompt_parts.append(f"User Query: {prompt}")
        
        return "\n\n".join(prompt_parts)
