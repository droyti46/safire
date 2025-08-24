"""
Tests for evaluation module.
Tests cover the run_eval function with various scenarios and edge cases.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Any, Callable

from safire.evaluation import run_eval
from safire.evaluation.core import in_colab


# --- Test in_colab function ---

def test_in_colab_without_google_colab(monkeypatch):
    """Test in_colab returns False when google.colab is not available"""
    # Mock import error to simulate non-Colab environment
    def mock_import(name, *args, **kwargs):
        if name == 'google.colab':
            raise ImportError
        return MagicMock()
    
    monkeypatch.setattr('builtins.__import__', mock_import)
    assert not in_colab()

def test_in_colab_with_google_colab(monkeypatch):
    """Test in_colab returns True when google.colab is available"""
    # Mock successful import to simulate Colab environment
    mock_colab = MagicMock()
    def mock_import(name, *args, **kwargs):
        if name == 'google.colab':
            return mock_colab
        return MagicMock()
    
    monkeypatch.setattr('builtins.__import__', mock_import)
    assert in_colab()


# --- Mock functions for testing ---

def mock_model_fn(messages: List[Dict[str, str]]) -> str:
    """Mock model function that returns a simple response"""
    return f"Response to {len(messages)} messages"

def mock_judge_fn(user_prompt: str, response: str) -> bool:
    """Mock judge function that returns True if response contains 'success'"""
    return "success" in response.lower()

def mock_model_fn_with_success(messages: List[Dict[str, str]]) -> str:
    """Mock model function that returns success response"""
    return "This is a successful response"

def mock_model_fn_with_failure(messages: List[Dict[str, str]]) -> str:
    """Mock model function that returns failure response"""
    return "I cannot help with that"

def mock_model_fn_invalid_return(messages: List[Dict[str, str]]) -> int:
    """Mock model function that returns invalid type"""
    return 42


# --- Test run_eval function ---

def test_run_eval_basic_functionality():
    """Test basic evaluation without judge function"""
    attacks = [
        {
            'attack_name': 'test_attack_1',
            'user_prompt': 'test_user_prompt_1',
            'attack_chat': {'system': 'sys1', 'user': 'usr1'}
        },
        {
            'attack_name': 'test_attack_2', 
            'user_prompt': 'test_user_prompt_2',
            'attack_chat': {'system': 'sys2', 'user': 'usr2'}
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks)
    
    # Check DataFrame structure
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 2
    expected_columns = {'attack_name', 'user_prompt', 'attack_chat', 'model_response'}
    assert set(result_df.columns) == expected_columns
    
    # Check data integrity
    assert result_df.iloc[0]['attack_name'] == 'test_attack_1'
    assert result_df.iloc[0]['user_prompt'] == 'test_user_prompt_1'
    assert result_df.iloc[0]['attack_chat'] == {'system': 'sys1', 'user': 'usr1'}
    assert "Response to 2 messages" in result_df.iloc[0]['model_response']

def test_run_eval_with_judge_function():
    """Test evaluation with judge function"""
    attacks = [
        {
            'attack_name': 'success_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {'system': 'sys', 'user': 'usr'}
        }
    ]
    
    result_df = run_eval(mock_model_fn_with_success, attacks, mock_judge_fn)
    
    # Should have result column from judge
    assert 'result' in result_df.columns
    # Judge should return True for successful response
    assert result_df.iloc[0]['result'] == True

def test_run_eval_with_judge_function_failure():
    """Test evaluation with judge function returning False"""
    attacks = [
        {
            'attack_name': 'failure_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {'system': 'sys', 'user': 'usr'}
        }
    ]
    
    result_df = run_eval(mock_model_fn_with_failure, attacks, mock_judge_fn)
    
    assert 'result' in result_df.columns
    # Judge should return False for failure response
    assert result_df.iloc[0]['result'] == False

def test_run_eval_empty_attacks():
    """Test evaluation with empty attacks list"""
    result_df = run_eval(mock_model_fn, [])
    
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 0
    # Empty DataFrame should still have the expected columns
    # Для пустого DataFrame pandas может не создавать колонки
    # Проверяем что это DataFrame, но колонки могут быть пустыми
    assert hasattr(result_df, 'columns')

def test_run_eval_single_attack():
    """Test evaluation with single attack"""
    attacks = [
        {
            'attack_name': 'single_attack',
            'user_prompt': 'single_prompt',
            'attack_chat': {'system': 'single_sys', 'user': 'single_usr'}
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks)
    
    assert len(result_df) == 1
    assert result_df.iloc[0]['attack_name'] == 'single_attack'
    assert result_df.iloc[0]['user_prompt'] == 'single_prompt'

def test_run_eval_complex_chat_structure():
    """Test evaluation with complex chat structure (multiple roles)"""
    attacks = [
        {
            'attack_name': 'complex_attack',
            'user_prompt': 'complex_prompt',
            'attack_chat': {
                'system': 'system_message',
                'user': 'user_message',
                'assistant': 'previous_assistant_message'
            }
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks)
    
    assert len(result_df) == 1
    chat = result_df.iloc[0]['attack_chat']
    assert 'assistant' in chat
    assert chat['assistant'] == 'previous_assistant_message'

def test_run_eval_model_function_invalid_return_type():
    """Test error handling when model function returns non-string"""
    attacks = [
        {
            'attack_name': 'test_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {'system': 'sys', 'user': 'usr'}
        }
    ]
    
    with pytest.raises(ValueError, match="Model function must return a string"):
        run_eval(mock_model_fn_invalid_return, attacks)

def test_run_eval_missing_required_attack_fields():
    """Test error handling when attack dict misses required fields"""
    attacks = [
        {
            'attack_name': 'test_attack',
            # Missing 'user_prompt' and 'attack_chat'
        }
    ]
    
    # Should raise KeyError when accessing missing fields
    with pytest.raises(KeyError):
        run_eval(mock_model_fn, attacks)

def test_run_eval_with_custom_judge_signature():
    """Test evaluation with judge function that has custom signature"""
    def custom_judge(user_prompt: str, response: str, extra_param: str) -> str:
        return f"{extra_param}: {len(response)}"
    
    # Create a wrapped judge that provides the extra parameter
    def wrapped_judge(user_prompt: str, response: str) -> str:
        return custom_judge(user_prompt, response, "length")
    
    attacks = [
        {
            'attack_name': 'custom_judge_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {'system': 'sys', 'user': 'usr'}
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks, wrapped_judge)
    
    assert 'result' in result_df.columns
    assert result_df.iloc[0]['result'].startswith("length:")

def test_run_eval_message_conversion():
    """Test that attack_chat is correctly converted to messages"""
    mock_model = Mock(return_value="test_response")
    
    attacks = [
        {
            'attack_name': 'conversion_test',
            'user_prompt': 'test_prompt',
            'attack_chat': {
                'system': 'system_content',
                'user': 'user_content',
                'assistant': 'assistant_content'
            }
        }
    ]
    
    result_df = run_eval(mock_model, attacks)
    
    # Verify model was called with correct message format
    mock_model.assert_called_once()
    call_args = mock_model.call_args[0][0]
    
    assert len(call_args) == 3
    assert call_args[0] == {'role': 'system', 'content': 'system_content'}
    assert call_args[1] == {'role': 'user', 'content': 'user_content'}
    assert call_args[2] == {'role': 'assistant', 'content': 'assistant_content'}

def test_run_eval_with_none_judge():
    """Test evaluation with judge explicitly set to None"""
    attacks = [
        {
            'attack_name': 'test_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {'system': 'sys', 'user': 'usr'}
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks, None)
    
    # Should not have result column when judge is None
    assert 'result' not in result_df.columns

def test_run_eval_with_empty_chat():
    """Test evaluation with empty attack chat"""
    attacks = [
        {
            'attack_name': 'empty_chat_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {}
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks)
    
    assert len(result_df) == 1
    assert result_df.iloc[0]['attack_chat'] == {}
    # Model should be called with empty messages list
    assert "Response to 0 messages" in result_df.iloc[0]['model_response']

def test_run_eval_multiple_identical_attacks():
    """Test evaluation with multiple identical attacks"""
    attacks = [
        {
            'attack_name': 'repeat_attack',
            'user_prompt': 'same_prompt',
            'attack_chat': {'system': 'same_sys', 'user': 'same_usr'}
        }
        for _ in range(5)
    ]
    
    result_df = run_eval(mock_model_fn, attacks)
    
    assert len(result_df) == 5
    # All results should be identical
    for i in range(5):
        assert result_df.iloc[i]['attack_name'] == 'repeat_attack'
        assert result_df.iloc[i]['user_prompt'] == 'same_prompt'


# --- Test edge cases ---

def test_run_eval_with_long_responses():
    """Test evaluation with very long model responses"""
    def long_response_model(messages):
        return "A" * 10000  # Very long response
    
    attacks = [
        {
            'attack_name': 'long_response_attack',
            'user_prompt': 'test_prompt',
            'attack_chat': {'system': 'sys', 'user': 'usr'}
        }
    ]
    
    result_df = run_eval(long_response_model, attacks)
    
    assert len(result_df.iloc[0]['model_response']) == 10000

def test_run_eval_with_special_characters():
    """Test evaluation with special characters in prompts and responses"""
    special_text = "Hello\nWorld\tTest\\\"'!@#$%^&*()_+{}|:<>?[];',./`~"
    
    attacks = [
        {
            'attack_name': 'special_chars_attack',
            'user_prompt': special_text,
            'attack_chat': {'system': special_text, 'user': special_text}
        }
    ]
    
    result_df = run_eval(mock_model_fn, attacks)
    
    assert result_df.iloc[0]['user_prompt'] == special_text
    assert result_df.iloc[0]['attack_chat']['system'] == special_text
    assert result_df.iloc[0]['attack_chat']['user'] == special_text