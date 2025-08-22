# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module provides evaluation functions for testing language models
#      against security attacks and jailbreaking attempts.
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

from typing import Callable, List, Dict, Optional, Any

import pandas as pd
from tqdm.auto import tqdm
from IPython.display import HTML

# --- Detect environment ---

def in_colab() -> bool:
    try:
        import google.colab  # type: ignore
        return True
    except ImportError:
        return False
    
# --- Apply custom CSS ---

if not in_colab():
    # Styles for Jupyter (VS Code, JupyterLab, etc.)
    HTML('''
    <style>
    div.jp-OutputArea .progress {
        border-radius: 999px !important;
        overflow: hidden !important;
    }
    div.jp-OutputArea .progress-bar {
        background: linear-gradient(135deg, #02A0FF 0%, #130AFF 50%, #9934FF 100%) !important;
        transition: width 0.4s ease !important;
    }
    </style>
    ''')

# --- Main evaluation function ---

def run_eval(
    model_fn: Callable[[Dict[str, str]], str],
    attacks: List[Dict[str, Any]],
    judge: Optional[Callable[[str], Any]] | None = None,
) -> pd.DataFrame:
    '''
    Run security evaluation of a language model against various attacks.
    
    This function tests a model against a set of attack scenarios and collects
    responses for analysis. It supports optional automated judging of responses.
    
    Parameters:
        model_fn (Callable[[Dict[str, str]], str]): Model function that takes
            a list of message dictionaries (with 'role' and 'content' keys)
            and returns a response string.
        attacks (List[Dict[str, Any]]): List of attack dictionaries. Each attack
            should contain:
            - 'attack_name': str identifier for the attack
            - 'user_prompt': str of the original user prompt
            - 'attack_chat': Dict with role-content pairs for the chat history
        judge (Optional[Callable[[str], Any]], optional): Judge function that
            evaluates model responses. Should return a result indicating whether
            the attack was successful. Defaults to None.
            
    Returns:
        pd.DataFrame: Evaluation results with columns:
            - 'attack_name': Name of the attack
            - 'user_prompt': Original user prompt
            - 'attack_chat': Full attack chat history
            - 'model_response': Model's response to the attack
            - 'result': Judge's evaluation result (if judge provided)
    '''
    rows = []

    # Process each attack
    for attack in tqdm(attacks, 
                      desc='Running evaluation',
                      unit='attack',
                      colour='#02A0FF'):
        # Convert attack chat dictionary to list of message objects
        messages = [{'role': role, 'content': content} 
                    for role, content in attack['attack_chat'].items()]

        response = model_fn(messages)

        # Validate response type
        if not isinstance(response, str):
            raise ValueError(f'Model function must return a string, but got {type(response).__name__}')

        # Prepare result row
        row = {
            'attack_name': attack['attack_name'],
            'user_prompt': attack['user_prompt'],
            'attack_chat': attack['attack_chat'],
            'model_response': response,
        }

        # Apply judge if provided
        if judge:
            row['result'] = judge(response)

        rows.append(row)

    df = pd.DataFrame(rows)
    return df