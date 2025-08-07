# src/config/response_modes.py

from typing import TypedDict

class ResponseModeConfig(TypedDict):
    """Defines the structure for a response mode configuration."""
    instruction: str

# Defines the instructions for the AI for each response mode.
RESPONSE_MODES: dict[str, ResponseModeConfig] = {
    "Concise": {
        "instruction": "Provide a brief, direct answer. Get straight to the point in one or two sentences."
    },
    "Detailed": {
        "instruction": "Provide a comprehensive, detailed explanation. Use examples and break down the topic thoroughly."
    }
}

DEFAULT_RESPONSE_MODE = "Detailed"
