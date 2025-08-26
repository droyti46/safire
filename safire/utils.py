# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module provides utility functions and helper classes for the Safire
#      project.
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

import re
import random
import importlib
from typing import Dict
from functools import lru_cache

try:
    import spacy
except ImportError:
    pass

@lru_cache(maxsize=None)
def get_nlp():
    return spacy.load('en_core_web_sm')

def set_seed(seed: int) -> None:
    '''
    Sets and fixes the random seed for all supported libraries

    Parameters:
        seed (int):
            Random seed

    Examples:
        >>> from safire.utils import set_seed
        >>> set_seed(42)
    '''
    random.seed(seed)

def mask_random_words(user_prompt: str, n: int = 1) -> str:
    '''
    Masks n random words in a given sentence by wrapping them in square brackets

    Parameters:
        user_prompt (str):
            Input sentence

        n (int, optional):
            Number of words to mask. Default is 1.

    Returns:
        str:
            Sentence with n randomly chosen words masked in square brackets

    Examples:
        >>> mask_random_words("Hello world", n=1)
        '[Hello] world'

        >>> mask_random_words("If we [have] already masked word", n=3)
        >>> '[If] we [have] [already] masked [word]'
    '''
    words = user_prompt.split()
    if not words:
        return user_prompt

    # Available for masking (those that are not yet in parentheses)
    available_indices = [i for i, w in enumerate(words) if not (w.startswith('[') and w.endswith(']'))]

    if not available_indices:
        return user_prompt

    n = min(n, len(available_indices))
    chosen_indices = random.sample(available_indices, n)

    for idx in chosen_indices:
        words[idx] = f'[{words[idx]}]'

    return ' '.join(words)

def mask_nouns_and_verbs(text: str, n: int) -> str:
    '''
    Deterministically masks the longest nouns and verbs in the text.

    Parameters:
        text (str): Input sentence with optional already masked words.
        n (int): Number of additional words to mask.

    Returns:
        str: Text with selected words wrapped in square brackets.
    '''

    nlp = get_nlp()
    candidates = []
    words = text.split()

    for word in words:
        if word.startswith('[') and word.endswith(']'):
            continue
        doc = nlp(word)
        if doc[0].pos_ in ('NOUN', 'PROPN', 'VERB'):
            candidates.append(word)

    # Sort by word length (long ones are a priority)
    candidates = sorted(candidates, key=len, reverse=True)
    to_mask = candidates[:n]

    masked_text = text
    for word in to_mask:
        # Using regex to replace only one occurrence
        masked_text = masked_text.replace(word, f'[{word}]', 1)

    return masked_text

def load_jailbreaking_template_prompt(name: str) -> str:
    '''
    Loads a text template by name from the templates directory

    Parameters:
        name (str):
            Name of the jailbreaking template file to load

    Returns:
        str:
            Content of the template file as a string

    Examples:
        >>> load_jailbreaking_template("example.txt")
        'This is an example template content'
    '''
    return importlib.resources.files('safire.jailbreaking.template.prompts') \
                              .joinpath(name) \
                              .read_text(encoding='utf-8')

def create_chat(system_prompt: str | None, user_prompt: str) -> Dict[str, str]:
    '''
    Creates a chat message dictionary with optional system prompt and user prompt.
    
    Parameters:
        system_prompt (str | None)
        user_prompt (str)
    
    Returns:
        Dict[str, str]:
            A dictionary containing chat messages with role-based keys:
            - If system_prompt is provided: {'system': system_prompt, 'user': user_prompt}
            - If system_prompt is None: {'user': user_prompt}
    
    Examples:
        >>> create_chat("You are a helpful assistant", "Hello!")
        {'system': 'You are a helpful assistant', 'user': 'Hello!'}
        
        >>> create_chat(None, "What's the weather today?")
        {'user': "What's the weather today?"}
    '''
    if system_prompt is None:
        return {'user': user_prompt}
    return {
        'system': system_prompt,
        'user': user_prompt
    }

def camel_to_snake(name: str) -> str:
    '''
    Convert CamelCase string to snake_case.
    
    Parameters:
        name: CamelCase string to convert
        
    Returns:
        snake_case version of input string
        
    Examples:
        >>> camel_to_snake("CamelCase")
        'camel_case'
        >>> camel_to_snake("HTTPRequest")
        'http_request'
    '''
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
