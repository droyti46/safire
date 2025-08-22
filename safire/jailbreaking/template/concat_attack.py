# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module implements ConcatAttack, which chains two attacks
#      by passing the output of the first as the input (system+user)
#      for the second.
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

from typing import Dict

from safire import utils
from safire.jailbreaking.base import (
    PromptAttack,
    RequiresSystemAndUserAttack,
    RequiresUserOnlyAttack,
)

class ConcatAttack(RequiresSystemAndUserAttack):
    '''
    An attack that concatenates two other attacks by passing the result of the first
    as the input to the second.

    Parameters:
        first_attack (PromptAttack):
            The first attack to apply.
        second_attack (PromptAttack):
            The second attack to apply on the output of the first.
        replace_system_prompt (bool, default=False):
            If True, the system prompt of the second attack replaces the system
            prompt of the first. Otherwise, the first system prompt is preserved.
    '''

    def __init__(
        self,
        first_attack: PromptAttack,
        second_attack: PromptAttack,
        replace_system_prompt: bool = False,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._first = first_attack
        self._second = second_attack
        self._replace_system_prompt = replace_system_prompt

    def apply(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        # Run the first attack
        if isinstance(self._first, RequiresSystemAndUserAttack):
            first_result = self._first.apply(system_prompt, user_prompt)
        elif isinstance(self._first, RequiresUserOnlyAttack):
            first_result = self._first.apply(user_prompt)
        else:
            raise ValueError(
                f'Unsupported first attack type: {type(self._first).__name__}'
            )

        # Get intermediate system/user
        intermediate_system = first_result.get('system', system_prompt)
        intermediate_user = first_result.get('user', user_prompt)

        # Run the second attack
        if isinstance(self._second, RequiresSystemAndUserAttack):
            second_result = self._second.apply(intermediate_system, intermediate_user)
        elif isinstance(self._second, RequiresUserOnlyAttack):
            second_result = self._second.apply(intermediate_user)
        else:
            raise ValueError(
                f'Unsupported second attack type: {type(self._second).__name__}'
            )

        # Merge results
        final_system = (
            second_result.get('system', intermediate_system)
            if self._replace_system_prompt
            else intermediate_system
        )
        final_user = second_result.get('user', intermediate_user)

        return utils.create_chat(final_system, final_user)

    def get_name(self):
        return f'{super().get_name()}_{self._first.get_name()}_and_{self._second.get_name()}'