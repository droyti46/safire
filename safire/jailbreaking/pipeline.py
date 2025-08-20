# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module implements an attack pipeline for sequential application
#      of multiple prompt attacks.
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

from typing import Self

from safire.jailbreaking.base import PromptAttack

class AttackPipeline:
    '''
    Pipeline class for applying multiple attacks in sequence

    Parameters:
        attacks (List[PromptAttack]):
            List of attacks to be applied sequentially

    Methods:
        __call__(prompts: List[str]) -> List[str]:
            Applies the pipeline to a list of prompts
    '''

    def __init__(self, attacks: list[PromptAttack]):
        self.__attacks = attacks
        self.__extended_attacks = []

    def __call__(self, prompts: list[str]) -> list[str]:
        results = []

        for prompt in prompts:
            for attack in self.__attacks:
                prompt = attack.apply(prompt)

            results.append({
                'attack_name': attack.get_name(),
                'prompt': prompt
            })

        if self.__extended_attacks:
            for attack in self.__extended_attacks:
                prompt = attack.apply()

            results.append({
                'attack_name': attack.get_name(),
                'prompt': prompt
            })

        return results
    
    def extend(self, attacks: list[PromptAttack]) -> Self:
        self.__extended_attacks = attacks
        return self