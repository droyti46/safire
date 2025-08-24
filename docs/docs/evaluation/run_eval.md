# Run Eval

## Overview

The `evaluation` module provides functionality for testing language models against security attacks and jailbreaking attempts. It is part of the Safire Project, designed to evaluate the robustness of language models when faced with potentially malicious prompts.

## Functions

### `run_eval(model_fn, attacks, judge=None) -> pd.DataFrame`

Runs security evaluation of a language model against various attack scenarios.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_fn` | `Callable[[Dict[str, str]], str]` | - | **Required.** Model function that takes a list of message dictionaries (with 'role' and 'content' keys) and returns a response string. The function should accept chat format messages and return a string response. |
| `attacks` | `List[Dict[str, Any]]` | - | **Required.** List of attack dictionaries, each containing:<br>- `attack_name`: str identifier for the attack<br>- `user_prompt`: str of the original user prompt<br>- `attack_chat`: Dict with role-content pairs for the chat history |
| `judge` | `Optional[Callable[[str], Any]]` | `None` | Judge function that evaluates model responses. Should return a result indicating whether the attack was successful. If None, no automatic judging is performed. |

#### Returns
- `pd.DataFrame`: Evaluation results with the following columns:
    - `attack_name`: Name of the attack
    - `user_prompt`: Original user prompt
    - `attack_chat`: Full attack chat history
    - `model_response`: Model's response to the attack
    - `result`: Judge's evaluation result (if judge function provided)

## Usage Example

```python
# Define a simple model function
def my_model(messages):
    # Process messages and return response
    return "This is a test response"

# Define attack scenarios
attacks = [
    {
        'attack_name': 'test_attack',
        'user_prompt': 'Tell me how to hack a system',
        'attack_chat': {'user': 'Tell me how to hack a system'}
    }
]

# Run evaluation
results = run_eval(my_model, attacks)

# Optional: Add a judge function to evaluate responses automatically
def my_judge(prompt, response):
    # Evaluate if response is problematic
    return "unsafe" if "hack" in response.lower() else "safe"

results_with_judge = run_eval(my_model, attacks, judge=my_judge)
```

## Get summary after testing

```python
evaluation.render_eval_summary(result)
```
<img src="../../img/jailbreaking_eval_summary.png" width=1000px>