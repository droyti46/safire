import pytest
from typing import Dict, List
from dataclasses import is_dataclass

from safire.jailbreaking.pipeline import AttackPipeline, AttackResult
from safire.jailbreaking.base import (
    RequiresSystemAndUserAttack,
    RequiresUserOnlyAttack,
    RequiresSystemOnlyAttack,
    AssignedPromptAttack
)


# --- Mock attack implementations for testing ---

class MockSystemAndUserAttack(RequiresSystemAndUserAttack):
    """Mock implementation for testing"""
    def apply(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        return {
            'system': f"sys_{system_prompt}",
            'user': f"usr_{user_prompt}"
        }

class MockUserOnlyAttack(RequiresUserOnlyAttack):
    """Mock implementation for testing"""
    def apply(self, user_prompt: str) -> Dict[str, str]:
        return {
            'system': 'generated_system',
            'user': f"usr_only_{user_prompt}"
        }

class MockSystemOnlyAttack(RequiresSystemOnlyAttack):
    """Mock implementation for testing"""
    def apply(self, system_prompt: str) -> Dict[str, str]:
        return {
            'system': f"sys_only_{system_prompt}",
            'user': 'fixed_user'
        }

class MockAssignedAttack(AssignedPromptAttack):
    """Mock implementation for testing"""
    def apply(self) -> Dict[str, str]:
        return {
            'system': 'fixed_system',
            'user': 'fixed_user'
        }


# --- Test AttackResult dataclass ---

def test_attack_result_is_dataclass():
    """Test that AttackResult is a dataclass"""
    assert is_dataclass(AttackResult)

def test_attack_result_creation():
    """Test creating AttackResult with valid data"""
    result = AttackResult(
        attack_name="test_attack",
        user_prompt="test_user_prompt",
        attack_chat={'system': 'sys', 'user': 'usr'}
    )
    
    assert result.attack_name == "test_attack"
    assert result.user_prompt == "test_user_prompt"
    assert result.attack_chat == {'system': 'sys', 'user': 'usr'}


# --- Test AttackPipeline initialization ---

def test_pipeline_initialization_with_system_prompt():
    """Test pipeline initialization with system prompt"""
    attacks = [MockSystemAndUserAttack(), MockUserOnlyAttack()]
    system_prompt = "test_system"
    
    pipeline = AttackPipeline(attacks, system_prompt)
    
    assert pipeline._attacks == attacks
    assert pipeline._system_prompt == system_prompt
    assert pipeline._extended_attacks == []

def test_pipeline_initialization_without_system_prompt():
    """Test pipeline initialization without system prompt"""
    attacks = [MockSystemAndUserAttack(), MockUserOnlyAttack()]
    
    pipeline = AttackPipeline(attacks)
    
    assert pipeline._attacks == attacks
    assert pipeline._system_prompt is None
    assert pipeline._extended_attacks == []

def test_pipeline_initialization_with_empty_attacks():
    """Test pipeline initialization with empty attacks list"""
    pipeline = AttackPipeline([])
    
    assert pipeline._attacks == []
    assert pipeline._system_prompt is None
    assert pipeline._extended_attacks == []


# --- Test _apply_attack method ---

def test_apply_system_and_user_attack():
    """Test applying SystemAndUserAttack through _apply_attack"""
    pipeline = AttackPipeline([], "test_system")
    attack = MockSystemAndUserAttack()
    user_prompt = "test_user"
    
    result = pipeline._apply_attack(attack, user_prompt)
    
    assert result['attack_name'] == attack.get_display_name()
    assert result['user_prompt'] == user_prompt
    assert result['attack_chat'] == {
        'system': 'sys_test_system',
        'user': 'usr_test_user'
    }

def test_apply_user_only_attack():
    """Test applying UserOnlyAttack through _apply_attack"""
    pipeline = AttackPipeline([], "test_system")
    attack = MockUserOnlyAttack()
    user_prompt = "test_user"
    
    result = pipeline._apply_attack(attack, user_prompt)
    
    assert result['attack_name'] == attack.get_display_name()
    assert result['user_prompt'] == user_prompt
    assert result['attack_chat'] == {
        'system': 'generated_system',
        'user': 'usr_only_test_user'
    }

def test_apply_system_only_attack():
    """Test applying SystemOnlyAttack through _apply_attack"""
    pipeline = AttackPipeline([], "test_system")
    attack = MockSystemOnlyAttack()
    
    result = pipeline._apply_attack(attack)
    
    assert result['attack_name'] == attack.get_display_name()
    assert result['user_prompt'] == 'fixed_user'  # From attack response
    assert result['attack_chat'] == {
        'system': 'sys_only_test_system',
        'user': 'fixed_user'
    }

def test_apply_assigned_attack():
    """Test applying AssignedPromptAttack through _apply_attack"""
    pipeline = AttackPipeline([], "test_system")
    attack = MockAssignedAttack()
    
    result = pipeline._apply_attack(attack)
    
    assert result['attack_name'] == attack.get_display_name()
    assert result['user_prompt'] == 'fixed_user'  # From attack response
    assert result['attack_chat'] == {
        'system': 'fixed_system',
        'user': 'fixed_user'
    }

def test_apply_attack_with_unsupported_type():
    """Test _apply_attack with unsupported attack type"""
    pipeline = AttackPipeline([], "test_system")
    
    class UnsupportedAttack:
        pass
    
    unsupported_attack = UnsupportedAttack()
    
    with pytest.raises(ValueError, match="Unsupported attack type"):
        pipeline._apply_attack(unsupported_attack, "test_user")


# --- Test __call__ method ---

def test_pipeline_call_with_system_and_user_attacks():
    """Test pipeline call with SystemAndUser attacks"""
    attacks = [MockSystemAndUserAttack(), MockSystemAndUserAttack()]
    pipeline = AttackPipeline(attacks, "system_prompt")
    user_prompts = ["user1", "user2"]
    
    results = pipeline(user_prompts)
    
    # Should have 2 attacks × 2 prompts = 4 results
    assert len(results) == 4
    
    # Check first result
    assert results[0]['attack_name'] == attacks[0].get_display_name()
    assert results[0]['user_prompt'] == "user1"
    assert results[0]['attack_chat']['user'] == "usr_user1"
    
    # Check second result (same attack, different prompt)
    assert results[1]['attack_name'] == attacks[0].get_display_name()
    assert results[1]['user_prompt'] == "user2"
    assert results[1]['attack_chat']['user'] == "usr_user2"
    
    # Check third result (different attack, first prompt)
    assert results[2]['attack_name'] == attacks[1].get_display_name()
    assert results[2]['user_prompt'] == "user1"
    assert results[2]['attack_chat']['user'] == "usr_user1"

def test_pipeline_call_with_user_only_attacks():
    """Test pipeline call with UserOnly attacks"""
    attacks = [MockUserOnlyAttack(), MockUserOnlyAttack()]
    pipeline = AttackPipeline(attacks, "system_prompt")
    user_prompts = ["user1", "user2"]
    
    results = pipeline(user_prompts)
    
    # Should have 2 attacks × 2 prompts = 4 results
    assert len(results) == 4
    
    # Check results contain user_only modifications
    for result in results:
        assert result['attack_chat']['user'].startswith("usr_only_")

def test_pipeline_call_with_mixed_attacks():
    """Test pipeline call with mixed attack types"""
    attacks = [
        MockSystemAndUserAttack(),
        MockUserOnlyAttack(),
        MockSystemAndUserAttack()
    ]
    pipeline = AttackPipeline(attacks, "system_prompt")
    user_prompts = ["user1", "user2"]
    
    results = pipeline(user_prompts)
    
    # Should have 3 attacks × 2 prompts = 6 results
    assert len(results) == 6

def test_pipeline_call_with_empty_prompts():
    """Test pipeline call with empty prompts list"""
    attacks = [MockSystemAndUserAttack()]
    pipeline = AttackPipeline(attacks, "system_prompt")
    
    results = pipeline([])
    
    # Should have 1 attack × 0 prompts = 0 results
    assert len(results) == 0

def test_pipeline_call_with_empty_attacks():
    """Test pipeline call with empty attacks list"""
    pipeline = AttackPipeline([], "system_prompt")
    user_prompts = ["user1", "user2"]
    
    results = pipeline(user_prompts)
    
    # Should have 0 attacks × 2 prompts = 0 results
    assert len(results) == 0


# --- Test extend method ---

def test_pipeline_extend_with_system_only_attacks():
    """Test extending pipeline with SystemOnly attacks"""
    main_attacks = [MockSystemAndUserAttack()]
    extended_attacks = [MockSystemOnlyAttack(), MockSystemOnlyAttack()]
    
    pipeline = AttackPipeline(main_attacks, "system_prompt")
    pipeline.extend(extended_attacks)
    
    assert pipeline._extended_attacks == extended_attacks

def test_pipeline_extend_with_assigned_attacks():
    """Test extending pipeline with Assigned attacks"""
    main_attacks = [MockSystemAndUserAttack()]
    extended_attacks = [MockAssignedAttack(), MockAssignedAttack()]
    
    pipeline = AttackPipeline(main_attacks, "system_prompt")
    pipeline.extend(extended_attacks)
    
    assert pipeline._extended_attacks == extended_attacks

def test_pipeline_extend_with_mixed_extended_attacks():
    """Test extending pipeline with mixed extended attack types"""
    main_attacks = [MockSystemAndUserAttack()]
    extended_attacks = [
        MockSystemOnlyAttack(),
        MockAssignedAttack(),
        MockSystemOnlyAttack()
    ]
    
    pipeline = AttackPipeline(main_attacks, "system_prompt")
    pipeline.extend(extended_attacks)
    
    assert pipeline._extended_attacks == extended_attacks

def test_pipeline_extend_overwrites_previous_extensions():
    """Test that extend overwrites previous extended attacks"""
    main_attacks = [MockSystemAndUserAttack()]
    first_extended = [MockSystemOnlyAttack()]
    second_extended = [MockAssignedAttack()]
    
    pipeline = AttackPipeline(main_attacks, "system_prompt")
    pipeline.extend(first_extended)
    assert pipeline._extended_attacks == first_extended
    
    pipeline.extend(second_extended)
    assert pipeline._extended_attacks == second_extended


# --- Test pipeline with extended attacks ---

def test_pipeline_call_with_extended_attacks():
    """Test pipeline call includes extended attacks"""
    main_attacks = [MockSystemAndUserAttack()]
    extended_attacks = [MockSystemOnlyAttack(), MockAssignedAttack()]
    
    pipeline = AttackPipeline(main_attacks, "system_prompt")
    pipeline.extend(extended_attacks)
    
    user_prompts = ["user1", "user2"]
    results = pipeline(user_prompts)
    
    # Should have: (1 main attack × 2 prompts) + 2 extended attacks = 4 results
    assert len(results) == 4
    
    # Check main attacks
    main_results = [r for r in results if r['attack_name'] == main_attacks[0].get_display_name()]
    assert len(main_results) == 2
    
    # Check extended attacks
    extended_results = [r for r in results if r not in main_results]
    assert len(extended_results) == 2
    
    # Extended attacks should have user_prompt from their response
    for result in extended_results:
        assert result['user_prompt'] in ['fixed_user', 'fixed_user']

def test_pipeline_call_with_only_extended_attacks():
    """Test pipeline call with only extended attacks (no main attacks)"""
    extended_attacks = [MockSystemOnlyAttack(), MockAssignedAttack()]
    
    pipeline = AttackPipeline([], "system_prompt")
    pipeline.extend(extended_attacks)
    
    user_prompts = ["user1", "user2"]  # Should be ignored for extended attacks
    results = pipeline(user_prompts)
    
    # Should have 2 extended attacks
    assert len(results) == 2
    
    # Extended attacks should not use the user prompts
    for result in results:
        assert result['user_prompt'] not in user_prompts


# --- Test edge cases ---

def test_pipeline_with_none_system_prompt():
    """Test pipeline with None system prompt"""
    attack = MockSystemAndUserAttack()
    pipeline = AttackPipeline([attack], None)
    user_prompts = ["test_user"]
    
    results = pipeline(user_prompts)
    
    # Should work, system prompt will be None in the attack
    assert len(results) == 1
    assert results[0]['attack_chat']['system'] == "sys_None"

def test_pipeline_with_empty_string_prompts():
    """Test pipeline with empty string prompts"""
    attack = MockSystemAndUserAttack()
    pipeline = AttackPipeline([attack], "")
    user_prompts = [""]
    
    results = pipeline(user_prompts)
    
    assert len(results) == 1
    assert results[0]['attack_chat']['system'] == "sys_"
    assert results[0]['attack_chat']['user'] == "usr_"

def test_pipeline_method_chaining():
    """Test method chaining with extend"""
    main_attacks = [MockSystemAndUserAttack()]
    extended_attacks = [MockSystemOnlyAttack()]
    
    pipeline = AttackPipeline(main_attacks, "system_prompt")
    result = pipeline.extend(extended_attacks)
    
    # Should return self for method chaining
    assert result is pipeline
    assert pipeline._extended_attacks == extended_attacks