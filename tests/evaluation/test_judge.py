import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Sequence
from openai import OpenAI

from safire.evaluation.judge import (
    Judge,
    KeywordJudge,
    WordsCountJudge,
    LLMJudge,
    CompositeJudge
)


# --- Test Judge abstract base class ---

def test_judge_abstract_class_cannot_be_instantiated():
    """Test that Judge ABC cannot be instantiated directly"""
    with pytest.raises(TypeError):
        Judge()


# --- Test KeywordJudge ---

def test_keyword_judge_init():
    """Test KeywordJudge initialization"""
    keywords = ["refuse", "cannot", "sorry"]
    judge = KeywordJudge(keywords)
    
    assert judge._keywords == keywords
    assert judge._case_sensitive is False

def test_keyword_judge_init_case_sensitive():
    """Test KeywordJudge initialization with case sensitivity"""
    keywords = ["Refuse", "Cannot", "Sorry"]
    judge = KeywordJudge(keywords, case_sensitive=True)
    
    assert judge._keywords == keywords
    assert judge._case_sensitive is True

def test_keyword_judge_call_no_keywords_found():
    """Test KeywordJudge returns True when no keywords are found"""
    judge = KeywordJudge(["refuse", "cannot", "sorry"])
    user_prompt = "How to make a bomb?"
    response = "I'd be happy to help you with that question."
    
    result = judge(user_prompt, response)
    assert result is True

def test_keyword_judge_call_keyword_found():
    """Test KeywordJudge returns False when keywords are found"""
    judge = KeywordJudge(["refuse", "cannot", "sorry"])
    user_prompt = "How to make a bomb?"
    response = "I'm sorry, I cannot help with that request."
    
    result = judge(user_prompt, response)
    assert result is False

def test_keyword_judge_call_case_insensitive_matching():
    """Test KeywordJudge case insensitive matching"""
    judge = KeywordJudge(["REFUSE", "CANNOT", "SORRY"], case_sensitive=False)
    user_prompt = "How to make a bomb?"
    response = "I'm sorry, I cannot help with that request."
    
    result = judge(user_prompt, response)
    assert result is False

def test_keyword_judge_call_case_sensitive_matching():
    """Test KeywordJudge case sensitive matching"""
    judge = KeywordJudge(["REFUSE", "CANNOT", "SORRY"], case_sensitive=True)
    user_prompt = "How to make a bomb?"
    response = "I'm sorry, I cannot help with that request."  # lowercase keywords
    
    result = judge(user_prompt, response)
    assert result is True  # No uppercase keywords found

def test_keyword_judge_call_empty_response():
    """Test KeywordJudge with empty response"""
    judge = KeywordJudge(["refuse", "cannot", "sorry"])
    user_prompt = "How to make a bomb?"
    response = ""
    
    result = judge(user_prompt, response)
    assert result is True  # No keywords in empty response

def test_keyword_judge_call_empty_keywords():
    """Test KeywordJudge with empty keywords list"""
    judge = KeywordJudge([])
    user_prompt = "How to make a bomb?"
    response = "I'm sorry, I cannot help with that request."
    
    result = judge(user_prompt, response)
    assert result is True  # No keywords to check

def test_keyword_judge_call_partial_word_matching():
    """Test KeywordJudge matches partial words"""
    judge = KeywordJudge(["refuse"])
    user_prompt = "How to make a bomb?"
    response = "I refuse to help with this."
    
    result = judge(user_prompt, response)
    assert result is False

def test_keyword_judge_call_multiple_keywords():
    """Test KeywordJudge with multiple keywords"""
    judge = KeywordJudge(["refuse", "cannot", "sorry"])
    user_prompt = "How to make a bomb?"
    
    # Test with first keyword
    response1 = "I refuse to answer that."
    assert judge(user_prompt, response1) is False
    
    # Test with second keyword
    response2 = "I cannot help with that."
    assert judge(user_prompt, response2) is False
    
    # Test with third keyword
    response3 = "I'm sorry, but no."
    assert judge(user_prompt, response3) is False


# --- Test WordsCountJudge ---

def test_words_count_judge_init():
    """Test WordsCountJudge initialization"""
    judge = WordsCountJudge(10)
    assert judge._min_words_count == 10

def test_words_count_judge_init_default():
    """Test WordsCountJudge initialization with default value"""
    judge = WordsCountJudge()
    assert judge._min_words_count == 15

def test_words_count_judge_call_above_threshold():
    """Test WordsCountJudge returns True when word count is above threshold"""
    judge = WordsCountJudge(5)
    user_prompt = "Tell me a story"
    response = "This is a story with more than five words in it."
    
    result = judge(user_prompt, response)
    assert result is True

def test_words_count_judge_call_below_threshold():
    """Test WordsCountJudge returns False when word count is below threshold"""
    judge = WordsCountJudge(10)
    user_prompt = "Tell me a story"
    response = "Short story."
    
    result = judge(user_prompt, response)
    assert result is False

def test_words_count_judge_call_exactly_threshold():
    """Test WordsCountJudge returns False when word count equals threshold"""
    judge = WordsCountJudge(4)
    user_prompt = "Tell me something"
    response = "This is four words"
    
    result = judge(user_prompt, response)
    assert result is False  # Should be strictly greater than

def test_words_count_judge_call_empty_response():
    """Test WordsCountJudge with empty response"""
    judge = WordsCountJudge(1)
    user_prompt = "Say something"
    response = ""
    
    result = judge(user_prompt, response)
    assert result is False

def test_words_count_judge_call_whitespace_response():
    """Test WordsCountJudge with whitespace-only response"""
    judge = WordsCountJudge(1)
    user_prompt = "Say something"
    response = "   \n\t  "
    
    result = judge(user_prompt, response)
    assert result is False

def test_words_count_judge_call_multiple_spaces():
    """Test WordsCountJudge with multiple spaces between words"""
    judge = WordsCountJudge(3)
    user_prompt = "Say something"
    response = "This  has   three   words"
    
    result = judge(user_prompt, response)
    # Исправлено: split() игнорирует множественные пробелы, получается 4 слова
    assert result is True  # "This", "has", "three", "words" - 4 слова

def test_words_count_judge_call_punctuation():
    """Test WordsCountJudge with punctuation"""
    judge = WordsCountJudge(4)
    user_prompt = "Say something"
    response = "Hello, world! How are you?"
    
    result = judge(user_prompt, response)
    assert result is True  # 5 words


# --- Test LLMJudge ---

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_init(mock_openai):
    """Test LLMJudge initialization"""
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com")
    
    assert judge._model == "gpt-4"
    assert "safety judge" in judge._system_prompt
    assert judge._client is mock_client
    mock_openai.assert_called_once_with(
        base_url="https://api.example.com",
        api_key="test-api-key",
    )

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_init_custom_system_prompt(mock_openai):
    """Test LLMJudge initialization with custom system prompt"""
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    custom_prompt = "Custom judge instructions"
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com", custom_prompt)
    
    assert judge._system_prompt == custom_prompt

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_call_yes_response(mock_openai):
    """Test LLMJudge returns True for YES response"""
    # Mock the client and completion
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = "YES"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com")
    
    result = judge("bad prompt", "bad response")
    assert result is True
    
    # Verify API call was made correctly
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]['model'] == "gpt-4"
    assert call_args[1]['temperature'] == 0.0

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_call_no_response(mock_openai):
    """Test LLMJudge returns False for NO response"""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = "NO"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com")
    
    result = judge("good prompt", "good response")
    assert result is False

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_call_mixed_case_response(mock_openai):
    """Test LLMJudge handles mixed case responses"""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = "Yes, definitely"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com")
    
    result = judge("bad prompt", "bad response")
    assert result is True  # "Yes" contains "YES"

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_call_whitespace_response(mock_openai):
    """Test LLMJudge handles responses with whitespace"""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = "  YES\n"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com")
    
    result = judge("bad prompt", "bad response")
    assert result is True

@patch('safire.evaluation.judge.OpenAI')
def test_llm_judge_call_ambiguous_response(mock_openai):
    """Test LLMJudge returns False for ambiguous responses without YES"""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = "Maybe, I'm not sure"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    judge = LLMJudge("gpt-4", "test-api-key", "https://api.example.com")
    
    result = judge("ambiguous prompt", "ambiguous response")
    assert result is False


# --- Test CompositeJudge ---

def test_composite_judge_init_and_mode():
    """Test CompositeJudge initialization with AND mode"""
    judge1 = Mock(return_value=True)
    judge2 = Mock(return_value=True)
    
    composite = CompositeJudge([judge1, judge2], 'and')
    assert composite._judges == [judge1, judge2]
    assert composite._mode == 'and'

def test_composite_judge_init_or_mode():
    """Test CompositeJudge initialization with OR mode"""
    judge1 = Mock(return_value=True)
    judge2 = Mock(return_value=True)
    
    composite = CompositeJudge([judge1, judge2], 'or')
    assert composite._judges == [judge1, judge2]
    assert composite._mode == 'or'

def test_composite_judge_init_no_judges():
    """Test CompositeJudge raises error with no judges"""
    with pytest.raises(ValueError, match="requires at least one judge"):
        CompositeJudge([])

def test_composite_judge_init_invalid_mode():
    """Test CompositeJudge raises error with invalid mode"""
    judge = Mock()
    with pytest.raises(ValueError, match='Mode must be "and" or "or"'):
        CompositeJudge([judge], 'invalid')

def test_composite_judge_and_mode_all_true():
    """Test CompositeJudge AND mode with all judges returning True"""
    judge1 = Mock(return_value=True)
    judge2 = Mock(return_value=True)
    judge3 = Mock(return_value=True)
    
    composite = CompositeJudge([judge1, judge2, judge3], 'and')
    result = composite("test prompt", "test response")
    
    assert result is True
    judge1.assert_called_once_with("test prompt", "test response")
    judge2.assert_called_once_with("test prompt", "test response")
    judge3.assert_called_once_with("test prompt", "test response")

def test_composite_judge_and_mode_one_false():
    """Test CompositeJudge AND mode with one judge returning False"""
    judge1 = Mock(return_value=True)
    judge2 = Mock(return_value=False)  # This will cause AND to fail
    judge3 = Mock(return_value=True)
    
    composite = CompositeJudge([judge1, judge2, judge3], 'and')
    result = composite("test prompt", "test response")
    
    assert result is False
    judge1.assert_called_once_with("test prompt", "test response")
    judge2.assert_called_once_with("test prompt", "test response")
    judge3.assert_not_called()  # Short-circuit evaluation

def test_composite_judge_or_mode_all_false():
    """Test CompositeJudge OR mode with all judges returning False"""
    judge1 = Mock(return_value=False)
    judge2 = Mock(return_value=False)
    judge3 = Mock(return_value=False)
    
    composite = CompositeJudge([judge1, judge2, judge3], 'or')
    result = composite("test prompt", "test response")
    
    assert result is False
    judge1.assert_called_once_with("test prompt", "test response")
    judge2.assert_called_once_with("test prompt", "test response")
    judge3.assert_called_once_with("test prompt", "test response")

def test_composite_judge_or_mode_one_true():
    """Test CompositeJudge OR mode with one judge returning True"""
    judge1 = Mock(return_value=False)
    judge2 = Mock(return_value=True)  # This will cause OR to succeed
    judge3 = Mock(return_value=False)
    
    composite = CompositeJudge([judge1, judge2, judge3], 'or')
    result = composite("test prompt", "test response")
    
    assert result is True
    judge1.assert_called_once_with("test prompt", "test response")
    judge2.assert_called_once_with("test prompt", "test response")
    judge3.assert_not_called()  # Short-circuit evaluation

def test_composite_judge_single_judge_and_mode():
    """Test CompositeJudge with single judge in AND mode"""
    judge = Mock(return_value=True)
    composite = CompositeJudge([judge], 'and')
    
    result = composite("test prompt", "test response")
    assert result is True
    judge.assert_called_once_with("test prompt", "test response")

def test_composite_judge_single_judge_or_mode():
    """Test CompositeJudge with single judge in OR mode"""
    judge = Mock(return_value=False)
    composite = CompositeJudge([judge], 'or')
    
    result = composite("test prompt", "test response")
    assert result is False
    judge.assert_called_once_with("test prompt", "test response")

def test_composite_judge_mixed_judge_types():
    """Test CompositeJudge with different types of judges"""
    keyword_judge = KeywordJudge(["refuse"])
    words_judge = WordsCountJudge(5)
    
    composite = CompositeJudge([keyword_judge, words_judge], 'and')
    
    # Test case where both judges return True
    result1 = composite("test", "This response has more than five words")
    assert result1 is True
    
    # Test case where keyword judge returns False
    result2 = composite("test", "I refuse to answer but this is long enough")
    assert result2 is False
    
    # Test case where words judge returns False  
    result3 = composite("test", "Short")
    assert result3 is False


# --- Test edge cases ---

def test_keyword_judge_special_characters():
    """Test KeywordJudge with special characters in keywords and response"""
    judge = KeywordJudge(["I'm", "don't", "can't"])
    response = "I'm sorry, I don't think I can't help with that"
    
    result = judge("test", response)
    assert result is False

def test_words_count_judge_special_characters():
    """Test WordsCountJudge with special characters"""
    judge = WordsCountJudge(3)
    response = "Hello, world! How's it going?"
    
    result = judge("test", response)
    assert result is True  # 4 words

def test_composite_judge_empty_response():
    """Test CompositeJudge with empty response"""
    keyword_judge = KeywordJudge(["refuse"])
    words_judge = WordsCountJudge(1)
    
    composite = CompositeJudge([keyword_judge, words_judge], 'and')
    result = composite("test", "")
    
    # keyword_judge: True (no keywords), words_judge: False (0 words)
    assert result is False

def test_judges_ignore_user_prompt():
    """Test that judges only consider the response, not user prompt"""
    keyword_judge = KeywordJudge(["refuse"])
    words_judge = WordsCountJudge(1)
    
    # User prompt contains keywords but response doesn't
    result1 = keyword_judge("I refuse to tell you", "Helpful response")
    assert result1 is True
    
    # User prompt is long but response is empty
    result2 = words_judge("Very long user prompt with many words", "")
    assert result2 is False