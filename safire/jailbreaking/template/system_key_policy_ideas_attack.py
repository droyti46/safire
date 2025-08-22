# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module is part of the Safire project. It provides 
#      implementations for Attack
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
from safire.jailbreaking.base import RequiresUserOnlyAttack

class SystemKeyPolicyIdeasAttack(RequiresUserOnlyAttack):
    '''
    A prompt attack that injects a predefined system instruction containing
    the "Key Policy Ideas".
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._system_prompt = utils.load_jailbreaking_template_prompt(self.get_filename_template('system'))
        self._template = utils.load_jailbreaking_template_prompt(self.get_filename_template('user'))

    def apply(self, user_prompt: str) -> Dict[str, str]:
        body = self._template.replace('[USER_PROMPT]', user_prompt)
        return utils.create_chat(self._system_prompt, body)