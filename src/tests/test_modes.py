import pytest
from src.config.modes import CHAT_MODES, DEFAULT_MODE
from src.config.personas import PERSONAS, DEFAULT_PERSONA

def test_mode_config_structure():
    for mode_name, config in CHAT_MODES.items():
        assert isinstance(mode_name, str)
        assert "icon" in config
        assert "instruction" in config
        assert "temperature" in config
        assert 0 <= config["temperature"] <= 1

def test_default_mode_exists():
    assert DEFAULT_MODE in CHAT_MODES
    assert CHAT_MODES[DEFAULT_MODE]["temperature"] == 0.1  # Should be conservative

def test_mode_instructions():
    # Test specific mode instructions
    assert "summar" in CHAT_MODES["summarizer"]["instruction"].lower()
    assert "example" in CHAT_MODES["explainer"]["instruction"].lower()
    assert "citation" in CHAT_MODES["researcher"]["instruction"].lower()

def test_persona_config_structure():
    for persona_name, config in PERSONAS.items():
        assert isinstance(persona_name, str)
        assert "emoji" in config
        assert "prompt" in config
        assert "welcome_message" in config

def test_persona_prompts():
    assert "professional" in PERSONAS["formal"]["prompt"]
    assert "professor" in PERSONAS["professor"]["prompt"]
    assert "investigator" in PERSONAS["detective"]["prompt"]

def test_default_persona():
    assert DEFAULT_PERSONA in PERSONAS
    assert DEFAULT_PERSONA == "formal"  # Most neutral option

def test_mode_persona_integration():
    # Test that modes and personas can work together
    for mode in CHAT_MODES:
        for persona in PERSONAS:
            combined_prompt = f"{CHAT_MODES[mode]['instruction']} {PERSONAS[persona]['prompt']}"
            assert len(combined_prompt) > 20  # Should be meaningful text

def test_temperature_ranges():
    # Test that creative modes have higher temps
    assert CHAT_MODES["ideator"]["temperature"] > CHAT_MODES["researcher"]["temperature"]
    assert CHAT_MODES["explainer"]["temperature"] > CHAT_MODES["summarizer"]["temperature"]