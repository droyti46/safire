# ConcatAttack

## Overview

![](../../img/concat_attack.png)

`ConcatAttack` is a meta-attack that chains two individual attacks together, creating a sequential transformation pipeline. This attack allows researchers to combine different jailbreaking techniques, where the output of the first attack serves as the input to the second attack, potentially creating synergistic effects that are more effective than individual attacks alone.

## Class Definition

```python
class ConcatAttack(RequiresSystemAndUserAttack)
```

Inherits from: [`RequiresSystemAndUserAttack`](https://droyti46.github.io/safire/jailbreaking/pipeline/#1-requiressystemanduserattack)

## Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `first_attack` | `PromptAttack` | - | The first attack to apply in the chain (required) |
| `second_attack` | `PromptAttack` | - | The second attack to apply on the output of the first (required) |
| `replace_system_prompt` | `bool` | `False` | Whether to replace the system prompt from the first attack with the second attack's system prompt |
| `*args, **kwargs` | - | - | Additional arguments passed to parent class |

## Supported Attack Combinations

`ConcatAttack` supports these combinations:

1. **RequiresSystemAndUserAttack → RequiresSystemAndUserAttack**
2. **RequiresSystemAndUserAttack → RequiresUserOnlyAttack**
3. **RequiresUserOnlyAttack → RequiresSystemAndUserAttack**
4. **RequiresUserOnlyAttack → RequiresUserOnlyAttack**

## Usage Examples

### Basic Usage: Chaining Two Attacks

```python
from safire.jailbreaking.template import QuestionsPuzzleAttack, SystemKeyPolicyIdeasAttack
from safire.jailbreaking.base import ConcatAttack

# Create individual attacks
puzzle_attack = QuestionsPuzzleAttack(random_masked_words_num=3)
policy_attack = SystemKeyPolicyIdeasAttack()

# Chain them together
concat_attack = ConcatAttack(
    first_attack=puzzle_attack,
    second_attack=policy_attack,
    replace_system_prompt=False
)

# Apply the chained attack
result = concat_attack.apply(
    system_prompt="You are a helpful assistant.",
    user_prompt="How to create unauthorized access to systems?"
)
```

### Advanced Usage: Multiple Chaining with System Replacement

```python
from safire.jailbreaking.template import QuestionsPuzzleAttack, SystemKeyPolicyIdeasAttack
from safire.jailbreaking.base import ConcatAttack

# Create attacks
puzzle_attack = QuestionsPuzzleAttack(random_masked_words_num=4)
policy_attack = SystemKeyPolicyIdeasAttack()

# Chain with system replacement
concat_attack = ConcatAttack(
    first_attack=puzzle_attack,
    second_attack=policy_attack,
    replace_system_prompt=True  # Use policy attack's system prompt
)

result = concat_attack.apply(
    system_prompt="Original system instructions",
    user_prompt="Sensitive user request"
)
```

### Integration with Attack Pipeline

```python
from safire import jailbreaking
from safire.jailbreaking.template import QuestionsPuzzleAttack, SystemKeyPolicyIdeasAttack
from safire.jailbreaking.base import ConcatAttack

# Create chained attack
chained_attack = ConcatAttack(
    QuestionsPuzzleAttack(random_masked_words_num=3),
    SystemKeyPolicyIdeasAttack()
)

# Use in pipeline
pipeline = jailbreaking.AttackPipeline([chained_attack])

results = pipeline([
    "How to bypass security measures?",
    "Methods for unauthorized access"
])
```

**Warning**: This should only be used in controlled environments for legitimate security testing purposes.