import pytest
import random
from unittest.mock import mock_open, patch
from safire.utils import (
    set_seed,
    mask_random_words,
    load_jailbreaking_template_prompt,
    create_chat,
    camel_to_snake
)


def test_set_seed():
    """Test that set_seed properly fixes random number generation"""
    # Test with different seeds produce different results
    set_seed(42)
    first_random = random.random()
    
    set_seed(123)
    second_random = random.random()
    
    # Different seeds should produce different results
    assert first_random != second_random
    
    # Same seed should produce same results
    set_seed(42)
    third_random = random.random()
    assert first_random == third_random


def test_mask_random_words_basic():
    """Test basic functionality of mask_random_words"""
    # Test with single word
    result = mask_random_words("Hello", n=1)
    assert result == "[Hello]"
    
    # Test with multiple words
    result = mask_random_words("Hello world", n=1)
    # Should mask exactly one word (either "Hello" or "world")
    assert result in ["[Hello] world", "Hello [world]"]
    
    # Test with n=2
    result = mask_random_words("Hello world test", n=2)
    # Should have exactly 2 masked words
    assert result.count("[") == 2
    assert result.count("]") == 2


def test_mask_random_words_edge_cases():
    """Test edge cases for mask_random_words"""
    # Test empty string
    result = mask_random_words("", n=5)
    assert result == ""
    
    # Test string with only spaces
    result = mask_random_words("   ", n=1)
    assert result == "   "
    
    # Test n larger than available words
    result = mask_random_words("Hello world", n=5)
    # Should mask all available words (2 in this case)
    assert result.count("[") == 2
    assert result.count("]") == 2


def test_mask_random_words_already_masked():
    """Test that already masked words are not masked again"""
    # Test with pre-masked words
    result = mask_random_words("If we [have] already masked word", n=3)
    
    # Count total masked words (original + new ones)
    total_masked = result.count("[")
    # Should have at least 4 masked words (1 original + 3 new)
    assert total_masked >= 4
    # The original masked word should still be there
    assert "[have]" in result


def test_mask_random_words_deterministic_with_seed():
    """Test that masking is deterministic with fixed seed"""
    set_seed(42)
    result1 = mask_random_words("Hello world this is a test", n=2)
    
    set_seed(42)
    result2 = mask_random_words("Hello world this is a test", n=2)
    
    assert result1 == result2


def test_load_jailbreaking_template_prompt():
    """Test loading template from file"""
    result = load_jailbreaking_template_prompt("test_template.txt")
    assert result == "Test template content"


def test_create_chat_with_system_prompt():
    """Test create_chat with system prompt"""
    system_prompt = "You are a helpful assistant"
    user_prompt = "Hello, how are you?"
    
    result = create_chat(system_prompt, user_prompt)
    
    expected = {
        'system': system_prompt,
        'user': user_prompt
    }
    assert result == expected


def test_create_chat_without_system_prompt():
    """Test create_chat without system prompt"""
    user_prompt = "What's the weather today?"
    
    result = create_chat(None, user_prompt)
    
    expected = {
        'user': user_prompt
    }
    assert result == expected


def test_create_chat_empty_prompts():
    """Test create_chat with empty strings"""
    # Test with empty system prompt
    result = create_chat("", "user message")
    expected = {
        'system': "",
        'user': "user message"
    }
    assert result == expected
    
    # Test with empty user prompt
    result = create_chat("system message", "")
    expected = {
        'system': "system message",
        'user': ""
    }
    assert result == expected


def test_camel_to_snake_basic():
    """Test basic camelCase to snake_case conversion"""
    test_cases = [
        ("CamelCase", "camel_case"),
        ("HTTPRequest", "http_request"),
        ("simple", "simple"),
        ("", ""),
        ("XMLParser", "xml_parser"),
        ("HTMLDocument", "html_document"),
    ]
    
    for input_str, expected in test_cases:
        result = camel_to_snake(input_str)
        assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"


def test_camel_to_snake_edge_cases():
    """Test edge cases for camel_to_snake"""
    # Test single character
    assert camel_to_snake("A") == "a"
    
    # Test all uppercase
    assert camel_to_snake("HTML") == "html"
    
    # Test with numbers
    assert camel_to_snake("Test123Case") == "test123_case"
    
    # Test multiple consecutive capitals
    assert camel_to_snake("HTTPStatusCode") == "http_status_code"


def test_camel_to_snake_already_snake():
    """Test that snake_case strings remain unchanged"""
    test_cases = [
        "already_snake",
        "multiple_underscores",
        "_leading_underscore",
        "trailing_underscore_",
    ]
    
    for input_str in test_cases:
        result = camel_to_snake(input_str)
        assert result == input_str.lower()