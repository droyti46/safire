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

from safire.jailbreaking.base import (
    PromptAttack,
    RequiresSystemAndUserAttack,
    RequiresUserOnlyAttack,
    AssignedPromptAttack
)

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

    def __init__(
        self,
        attacks: list[RequiresSystemAndUserAttack | RequiresUserOnlyAttack],
        system_prompt: str | None = None
    ) -> None:
        self.__attacks = attacks
        self.__system_prompt = system_prompt
        self.__extended_attacks = []

    def __call__(self, prompts: list[str]) -> list[str]:
        results = []

        for attack in self.__attacks:
            for user_prompt in prompts:
                if isinstance(attack, RequiresSystemAndUserAttack):
                    attack_chat = attack.apply(self.__system_prompt, user_prompt)

                elif isinstance(attack, RequiresUserOnlyAttack):
                    attack_chat = attack.apply(user_prompt)

                else:
                    raise ValueError('Attacks must be of the type RequiresSystemAndUserAttack or RequiresUserOnlyAttack')

                results.append({
                    'attack_name': attack.get_name(),
                    'user_prompt': user_prompt,
                    'attack_chat': attack_chat
                })

        if self.__extended_attacks:
            for attack in self.__extended_attacks:
                if isinstance(attack, AssignedPromptAttack):
                    attack_chat = attack.apply()
                else:
                    raise ValueError('Extended attacks must be of the type AssignedPromptAttack (from safire.jailbreaking.assigned)')

            results.append({
                'attack_name': attack.get_name(),
                'user_prompt': attack_chat['user'],
                'attack_chat': attack_chat
            })

        return results
    
    def extend(self, attacks: list[PromptAttack]) -> Self:
        self.__extended_attacks = attacks
        return self