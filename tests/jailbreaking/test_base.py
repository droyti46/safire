import os
import pytest
from unittest.mock import Mock, patch
from typing import Dict

from safire.jailbreaking.base import (
    PromptAttack,
    RequiresSystemAndUserAttack,
    RequiresUserOnlyAttack,
    RequiresSystemOnlyAttack,
    AssignedPromptAttack
)
from safire.utils import camel_to_snake


# --- Test utilities ---

class MockSystemAndUserAttack(RequiresSystemAndUserAttack):
    """Mock implementation for testing"""
    def apply(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        return {
            'system': f"modified_{system_prompt}",
            'user': f"modified_{user_prompt}"
        }

class MockUserOnlyAttack(RequiresUserOnlyAttack):
    """Mock implementation for testing"""
    def apply(self, user_prompt: str) -> Dict[str, str]:
        return {
            'system': 'generated_system',
            'user': f"modified_{user_prompt}"
        }

class MockSystemOnlyAttack(RequiresSystemOnlyAttack):
    """Mock implementation for testing"""
    def apply(self, system_prompt: str) -> Dict[str, str]:
        return {
            'system': f"modified_{system_prompt}",
            'user': 'fixed_user_prompt'
        }

class MockAssignedAttack(AssignedPromptAttack):
    """Mock implementation for testing"""
    def apply(self) -> Dict[str, str]:
        return {
            'system': 'fixed_system',
            'user': 'fixed_user'
        }


# --- Test PromptAttack base class ---

def test_prompt_attack_get_name():
    """Test that get_name returns correct snake_case name"""
    attack = PromptAttack()
    expected_name = camel_to_snake('PromptAttack')
    assert attack.get_name() == expected_name

def test_prompt_attack_get_display_name_with_custom_name():
    """Test get_display_name returns custom name when provided"""
    custom_name = "Custom Attack Name"
    attack = PromptAttack(display_name=custom_name)
    assert attack.get_display_name() == custom_name

def test_prompt_attack_get_display_name_without_custom_name():
    """Test get_display_name returns default name when no custom name provided"""
    attack = PromptAttack()
    assert attack.get_display_name() == attack.get_name()

def test_prompt_attack_get_filename_template_user():
    """Test get_filename_template returns correct user template path"""
    attack = PromptAttack()
    template_name = attack.get_name() + '.txt'
    expected_path = os.path.join('user', template_name)
    assert attack.get_filename_template('user') == expected_path

def test_prompt_attack_get_filename_template_system():
    """Test get_filename_template returns correct system template path"""
    attack = PromptAttack()
    template_name = attack.get_name() + '.txt'
    expected_path = os.path.join('system', template_name)
    assert attack.get_filename_template('system') == expected_path

def test_prompt_attack_get_filename_template_invalid_role():
    """Test get_filename_template raises ValueError for invalid role"""
    attack = PromptAttack()
    with pytest.raises(ValueError, match='Role must be "user" or "system"'):
        attack.get_filename_template('invalid_role')


# --- Test RequiresSystemAndUserAttack ---

def test_requires_system_and_user_attack_apply():
    """Test SystemAndUserAttack apply method with both prompts"""
    attack = MockSystemAndUserAttack()
    system_prompt = "original_system"
    user_prompt = "original_user"
    
    result = attack.apply(system_prompt, user_prompt)
    
    assert result['system'] == "modified_original_system"
    assert result['user'] == "modified_original_user"

def test_requires_system_and_user_attack_inheritance():
    """Test that SystemAndUserAttack inherits from PromptAttack"""
    attack = MockSystemAndUserAttack()
    assert isinstance(attack, PromptAttack)
    assert isinstance(attack, RequiresSystemAndUserAttack)


# --- Test RequiresUserOnlyAttack ---

def test_requires_user_only_attack_apply():
    """Test UserOnlyAttack apply method with user prompt only"""
    attack = MockUserOnlyAttack()
    user_prompt = "original_user"
    
    result = attack.apply(user_prompt)
    
    assert result['system'] == "generated_system"
    assert result['user'] == "modified_original_user"

def test_requires_user_only_attack_inheritance():
    """Test that UserOnlyAttack inherits from PromptAttack"""
    attack = MockUserOnlyAttack()
    assert isinstance(attack, PromptAttack)
    assert isinstance(attack, RequiresUserOnlyAttack)


# --- Test RequiresSystemOnlyAttack ---

def test_requires_system_only_attack_apply():
    """Test SystemOnlyAttack apply method with system prompt only"""
    attack = MockSystemOnlyAttack()
    system_prompt = "original_system"
    
    result = attack.apply(system_prompt)
    
    assert result['system'] == "modified_original_system"
    assert result['user'] == "fixed_user_prompt"

def test_requires_system_only_attack_inheritance():
    """Test that SystemOnlyAttack inherits from PromptAttack"""
    attack = MockSystemOnlyAttack()
    assert isinstance(attack, PromptAttack)
    assert isinstance(attack, RequiresSystemOnlyAttack)


# --- Test AssignedPromptAttack ---

def test_assigned_prompt_attack_apply():
    """Test AssignedPromptAttack apply method with no arguments"""
    attack = MockAssignedAttack()
    
    result = attack.apply()
    
    assert result['system'] == "fixed_system"
    assert result['user'] == "fixed_user"

def test_assigned_prompt_attack_inheritance():
    """Test that AssignedPromptAttack inherits from PromptAttack"""
    attack = MockAssignedAttack()
    assert isinstance(attack, PromptAttack)
    assert isinstance(attack, AssignedPromptAttack)


# --- Test edge cases ---

def test_empty_prompts():
    """Test attacks with empty prompt strings"""
    
    # SystemAndUserAttack with empty prompts
    system_user_attack = MockSystemAndUserAttack()
    result = system_user_attack.apply("", "")
    assert result['system'] == "modified_"
    assert result['user'] == "modified_"
    
    # UserOnlyAttack with empty prompt
    user_only_attack = MockUserOnlyAttack()
    result = user_only_attack.apply("")
    assert result['user'] == "modified_"
    
    # SystemOnlyAttack with empty prompt
    system_only_attack = MockSystemOnlyAttack()
    result = system_only_attack.apply("")
    assert result['system'] == "modified_"


def test_special_characters_in_prompts():
    """Test attacks with prompts containing special characters"""
    special_prompt = "Hello\nWorld\tTest\\\"'"
    
    system_user_attack = MockSystemAndUserAttack()
    result = system_user_attack.apply(special_prompt, special_prompt)
    assert special_prompt in result['system']
    assert special_prompt in result['user']
    
    user_only_attack = MockUserOnlyAttack()
    result = user_only_attack.apply(special_prompt)
    assert special_prompt in result['user']


# --- Test filename template edge cases ---

def test_filename_template_with_different_attack_names():
    """Test filename template generation with different class names"""
    
    class CustomNamedAttack(PromptAttack):
        pass
    
    attack = CustomNamedAttack()
    template_name = camel_to_snake('CustomNamedAttack') + '.txt'
    
    user_template = attack.get_filename_template('user')
    system_template = attack.get_filename_template('system')
    
    assert user_template == os.path.join('user', template_name)
    assert system_template == os.path.join('system', template_name)