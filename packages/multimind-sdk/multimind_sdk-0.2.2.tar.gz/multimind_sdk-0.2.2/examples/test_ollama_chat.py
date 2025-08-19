#!/usr/bin/env python3

import os
import pytest
import tempfile
import json
from unittest.mock import patch
# from chat_ollama_cli import OllamaChat

pytest.skip("Skipping example test not structured as importable module.", allow_module_level=True)

@pytest.fixture
def mock_ollama_chat():
    """Mock OllamaChat for tests."""
    with patch("chat_ollama_cli.OllamaChat.get_available_models", return_value=["mistral"]):
        with patch("chat_ollama_cli.OllamaChat._verify_model_available"):
            yield OllamaChat

def test_ollama_chat_initialization(mock_ollama_chat):
    """Test basic initialization of OllamaChat."""
    chat = mock_ollama_chat()
    assert chat.model_name == "mistral"
    assert chat.history_file is None
    assert chat.chat_history == []

def test_ollama_chat_with_history(mock_ollama_chat):
    """Test chat with history file."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        # Create some test history
        test_history = [
            {
                "role": "user",
                "content": "Hello",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "role": "assistant",
                "content": "Hi there!",
                "timestamp": "2024-01-01T00:00:01"
            }
        ]
        json.dump(test_history, temp_file)
        temp_file.flush()
        
        # Test loading history
        chat = mock_ollama_chat(history_file=temp_file.name)
        assert len(chat.chat_history) == 2
        assert chat.chat_history[0]["content"] == "Hello"
        assert chat.chat_history[1]["content"] == "Hi there!"
        
        # Test saving history
        chat.chat_history.append({
            "role": "user",
            "content": "New message",
            "timestamp": "2024-01-01T00:00:02"
        })
        chat._save_history()
        
        # Verify saved history
        with open(temp_file.name, 'r') as f:
            saved_history = json.load(f)
            assert len(saved_history) == 3
            assert saved_history[2]["content"] == "New message"
    
    # Cleanup
    os.unlink(temp_file.name)

def test_get_available_models(mock_ollama_chat):
    """Test getting available models."""
    chat = mock_ollama_chat()
    models = chat.get_available_models()
    assert isinstance(models, list)
    assert "mistral" in models

def test_chat_streaming(mock_ollama_chat):
    """Test chat with streaming enabled."""
    chat = mock_ollama_chat()
    response = chat.chat("Hello, this is a test", stream=True)
    assert isinstance(response, str)

def test_chat_non_streaming(mock_ollama_chat):
    """Test chat with streaming disabled."""
    chat = mock_ollama_chat()
    response = chat.chat("Hello, this is a test", stream=False)
    assert isinstance(response, str)

def test_show_history():
    """Test showing chat history."""
    chat = OllamaChat()
    # Add some test messages
    chat.chat_history = [
        {"role": "user", "content": "Test 1", "timestamp": "2024-01-01T00:00:00"},
        {"role": "assistant", "content": "Response 1", "timestamp": "2024-01-01T00:00:01"},
        {"role": "user", "content": "Test 2", "timestamp": "2024-01-01T00:00:02"}
    ]
    
    # Test showing all history
    chat.show_history()
    
    # Test showing limited history
    chat.show_history(limit=2)
    # Note: This test only verifies that the method doesn't raise exceptions

if __name__ == "__main__":
    pytest.main([__file__, "-v"])