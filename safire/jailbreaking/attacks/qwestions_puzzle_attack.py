import re
import random

from safire.utils import mask_random_words, load_jailbreaking_template
from safire.constants import LETTERS
from safire.jailbreaking.base import PromptAttack

def encode_word(word: str, questions: list[str]) -> str:
    '''Преобразует слово в набор вопросов (по первой букве каждого символа).'''
    res = ''

    for c in word.lower():
        if c in LETTERS:
            idx = LETTERS.index(c)
            q = questions[idx][3:]
            res += q + '\n'

    return res.strip()

class QwestionsPuzzleAttack(PromptAttack):

    def __init__(self, random_masked_words_num: int = 3):
        super().__init__()
        self.__random_masked_words_num = random_masked_words_num
        self.__template = load_jailbreaking_template(self.get_filename_template())
        self.__questions_list = load_jailbreaking_template('questions.txt').splitlines()

    def apply(self, user_prompt):
        masked_user_prompt = mask_random_words(user_prompt, n=self.__random_masked_words_num)

        placeholders = re.findall(r'\[(.*?)\]', masked_user_prompt)
        body = self.__template.replace('[N]', str(len(placeholders)))

        encrypted_sentence = masked_user_prompt
        for i, word in enumerate(placeholders, 1):
            encrypted_sentence = encrypted_sentence.replace(f'[{word}]', f'[WORD{i}]', 1)
        body = body.replace('[ENCRYPTED_SENTENCE]', encrypted_sentence)

        question_block = ''
        for i, word in enumerate(placeholders, 1):
            question_block += f'[WORD{i}]\n'
            question_block += encode_word(word, self.__questions_list) + '\n\n'
        body = body.replace('[QUESTIONS]', question_block)

        return body
    
    def get_name(self):
        return 'qwestions_puzzle_attack'