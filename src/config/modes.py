from typing import TypedDict

class ModeConfig(TypedDict):
    icon: str
    instruction: str
    temperature: float

CHAT_MODES: dict[str, ModeConfig] = {
    "summarizer": {
        "icon": "🧾",
        "instruction": "Provide concise bullet-point summaries under 100 words. Focus on key facts and actions.",
        "temperature": 0.1
    },
    "explainer": {
        "icon": "🧠", 
        "instruction": "Break down complex concepts into simple terms with examples. Use analogies when helpful.",
        "temperature": 0.3
    },
    "ideator": {
        "icon": "💡",
        "instruction": "Generate creative ideas and solutions. Encourage brainstorming with multiple options.",
        "temperature": 0.7
    },
    "tutor": {
        "icon": "📚",
        "instruction": "Teach concepts step-by-step. Provide quizzes and practical exercises.",
        "temperature": 0.2
    },
    "researcher": {
        "icon": "🔍",
        "instruction": "Provide detailed, citation-backed answers. Always reference sources.",
        "temperature": 0.1
    }
}

DEFAULT_MODE = "researcher"