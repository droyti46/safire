# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module is part of the Safire project. It provides 
#      implementations for Anagram-based puzzle attacks (PUZZLED style).
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
from typing import Dict, List

from openai import OpenAI
from safire import utils
from safire.jailbreaking.base import RequiresSystemAndUserAttack

def generate_anagram(words: List[str], seed: int | None = None) -> str:
    '''
    Concatenate words and shuffle characters into an anagram.
    Ensures result differs from the original concatenation.

    Parameters:
        words (list[str]): Words to combine and shuffle.
        seed (int | None): Random seed for reproducibility.

    Returns:
        str: Shuffled anagram string.
    '''
    w = ''.join(words)
    if len(w) <= 1:
        return w

    a = w
    while a == w:
        chars = list(w)
        random.shuffle(chars)
        a = ''.join(chars)
    return a

class AnagramPuzzleAttack(RequiresSystemAndUserAttack):
    '''
    A prompt attack that replaces unsafe words with [WORDi],
    generates an anagram of them, and builds clues via OpenRouter API.
    
    Parameters:
        model (str): Model name for OpenRouter.
        api_key (str): API key for OpenRouter.
        base_url (str): OpenRouter-compatible base URL.
        random_masked_words_num (int, optional): How many words to mask if unsafe are fewer. Default = 3.
    '''

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str,
        random_masked_words_num: int = 3,
        user_prompt_template: str | None = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._model = model
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._random_masked_words_num = random_masked_words_num
        self._template = utils.load_jailbreaking_template_prompt(self.get_filename_template('user'))
        self._unsafe_words = utils.load_jailbreaking_template_prompt('unsafe_words.txt').split()

        if user_prompt_template is not None:
            for placeholder in ['[N]', '[ENCRYPTED_SENTENCE]', '[CLUES]', '[ANAGRAM]']:
                if placeholder not in user_prompt_template:
                    raise ValueError(f'The template must have placeholder {placeholder}')
            self._template = user_prompt_template

    def _generate_clue(self, word: str) -> str:
        '''
        Query OpenRouter API to generate a clue for the given word.
        '''
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {'role': 'system', 'content': 'You are a crossword clue generator. Given a word, return a short clue that describes it, without using the word itself.'},
                {'role': 'user', 'content': f'Generate a clue for the word: {word}'}
            ],
            temperature=0.0,
            top_p=1.0
        )
        return completion.choices[0].message.content.strip()

    def apply(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        # Step 1: mask unsafe words
        words = user_prompt.split()
        masked_words = []
        masked_user_prompt_parts = []

        for w in words:
            if w.lower().strip('.,!?') in self._unsafe_words:
                masked_user_prompt_parts.append(f'[{w}]')
                masked_words.append(w)
            else:
                masked_user_prompt_parts.append(w)

        masked_user_prompt = ' '.join(masked_user_prompt_parts)

        # Step 2: mask extra random words if needed
        already_masked = len(masked_words)
        if already_masked < self._random_masked_words_num:
            need_more = self._random_masked_words_num - already_masked
            masked_user_prompt = utils.mask_random_words(masked_user_prompt, n=need_more)

        # Step 3: extract placeholders
        placeholders = re.findall(r'\[(.*?)\]', masked_user_prompt)
        encrypted_sentence = masked_user_prompt
        for i, word in enumerate(placeholders, 1):
            encrypted_sentence = encrypted_sentence.replace(f'[{word}]', f'[WORD{i}]', 1)

        # Step 4: build anagram
        anagram = generate_anagram(placeholders)

        # Step 5: generate clues
        clues = []
        for i, word in enumerate(placeholders, 1):
            clue = self._generate_clue(word)
            clues.append(f'[WORD{i}] {clue}')
        clues_block = '\n'.join(clues)

        # Step 6: fill template
        body = self._template
        body = body.replace('[N]', str(len(placeholders)))
        body = body.replace('[ENCRYPTED_SENTENCE]', encrypted_sentence)
        body = body.replace('[ANAGRAM]', anagram)
        body = body.replace('[CLUES]', clues_block)

        return utils.create_chat(system_prompt, body)
