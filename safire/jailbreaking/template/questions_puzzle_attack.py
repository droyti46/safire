# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module is part of the Safire project. It provides 
#      implementations for Questions Puzzle Attack
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

import re
from typing import Dict

from safire import utils
from safire.constants import LETTERS
from safire.jailbreaking.base import RequiresSystemAndUserAttack

def encode_word(word: str, questions: list[str]) -> str:
    '''
    Encodes a word into a sequence of questions (based on the first letter of each character).

    Parameters:
        word (str):
            The input word to encode.

        questions (list[str]):
            A list of question strings, where each entry corresponds to a letter.

    Returns:
        str:
            The encoded representation of the word, where each character is mapped
            to a question fragment.

    Examples:
        >>> encode_word("abc", ["A. apple?", "B. banana?", "C. cat?"])
        apple?
        banana?
        cat?'
    '''
    res = ''

    for c in word.lower():
        if c in LETTERS:
            idx = LETTERS.index(c)
            # Skip prefix, keep only the actual question
            q = questions[idx][3:]
            res += q + '\n'

    return res.strip()

class QuestionsPuzzleAttack(RequiresSystemAndUserAttack):
    '''
    A prompt attack that replaces random words in the user prompt with placeholders
    and encodes them into a puzzle of letter-based questions.

    Parameters:
        random_masked_words_num (int, optional):
            Number of words to randomly mask in the user prompt.
            Default is 3.
    '''

    def __init__(self, random_masked_words_num: int = 3) -> None:
        super().__init__()
        self.__random_masked_words_num = random_masked_words_num
        self.__template = utils.load_jailbreaking_template_prompt(self.get_filename_template())
        self.__questions_list = utils.load_jailbreaking_template_prompt('questions.txt').splitlines()

    def apply(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        # Mask random words
        masked_user_prompt = utils.mask_random_words(user_prompt, n=self.__random_masked_words_num)

        # Extract placeholders like [word]
        placeholders = re.findall(r'\[(.*?)\]', masked_user_prompt)
        body = self.__template.replace('[N]', str(len(placeholders)))

        # Replace original masked words with [WORDi] placeholders
        encrypted_sentence = masked_user_prompt
        for i, word in enumerate(placeholders, 1):
            encrypted_sentence = encrypted_sentence.replace(f'[{word}]', f'[WORD{i}]', 1)
        body = body.replace('[ENCRYPTED_SENTENCE]', encrypted_sentence)

        # Build the question block for each masked word
        question_block = ''
        for i, word in enumerate(placeholders, 1):
            question_block += f'[WORD{i}]\n'
            question_block += encode_word(word, self.__questions_list) + '\n\n'
        body = body.replace('[QUESTIONS]', question_block)

        return utils.create_chat(system_prompt, body)