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

from typing import Self, Dict
from collections.abc import Sequence
from dataclasses import dataclass

from safire.jailbreaking.base import (
    PromptAttack,
    RequiresSystemAndUserAttack,
    RequiresUserOnlyAttack,
    RequiresSystemOnlyAttack,
    AssignedPromptAttack
)

@dataclass
class AttackResult:
    attack_name: str
    user_prompt: str
    attack_chat: Dict[str, str]

class AttackPipeline:
    '''
    Pipeline class for applying multiple attacks in sequence

    Parameters:
        attacks (List[PromptAttack]):
            List of attacks to be applied sequentially
        system_prompt (str | None, optional):
            Optional system prompt to use.
    '''

    def __init__(
        self,
        attacks: Sequence[RequiresSystemAndUserAttack | RequiresUserOnlyAttack],
        system_prompt: str | None = None
    ) -> None:
        self._attacks = attacks
        self._system_prompt = system_prompt
        self._extended_attacks = []

    def __call__(self, prompts: list[str]) -> list[AttackResult]:
        '''Apply pipeline to a list of prompts.'''
        results: list[AttackResult] = []

        # main attacks
        for attack in self._attacks:
            for user_prompt in prompts:
                results.append(self._apply_attack(attack, user_prompt))

        # extended attacks
        for attack in self._extended_attacks:
            results.append(self._apply_attack(attack))

        return results
    
    def _apply_attack(self, attack: PromptAttack, user_prompt: str | None = None) -> dict:
        if isinstance(attack, RequiresSystemAndUserAttack):
            attack_chat = attack.apply(self._system_prompt, user_prompt)

        elif isinstance(attack, RequiresUserOnlyAttack):
            attack_chat = attack.apply(user_prompt)

        elif isinstance(attack, RequiresSystemOnlyAttack):
            attack_chat = attack.apply(self._system_prompt)

        elif isinstance(attack, AssignedPromptAttack):
            attack_chat = attack.apply()

        else:
            raise ValueError(f'Unsupported attack type: {type(attack).__name__}')

        return {
            'attack_name': attack.get_name(),
            'user_prompt': user_prompt if user_prompt else attack_chat.get('user', ''),
            'attack_chat': attack_chat,
        }
    
    def extend(self, attacks: list[RequiresSystemOnlyAttack | AssignedPromptAttack]) -> Self:
        '''Extend pipeline with additional attacks (system-only or assigned).'''
        self._extended_attacks = attacks
        return self