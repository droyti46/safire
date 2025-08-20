# =============================================================================
#  Safire Library for testing of language models for jailbreaking
#
#  Description:
#      This module is part of the Safire project
#      It defines the abstract base classes for prompt attacks
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      Nikita Bakutov
# =============================================================================

from typing import Dict
from abc import ABC, abstractmethod

from safire.utils import camel_to_snake

__all__ = [
    'RequiresSystemAndUserAttack',
    'RequiresUserOnlyAttack',
    'AssignedPromptAttack'
]

class PromptAttack(ABC):
    '''
    Abstract class for attack
    '''

    def get_name(self) -> str:
        '''
        Returns the name of the attack.

        Returns:
            str: The attack identifier.
        '''
        return camel_to_snake(self.__class__.__name__)

    def get_filename_template(self) -> str:
        '''
        Returns the template filename of the attack.

        Returns:
            str: The attack template filename.
        '''
        return self.get_name() + '.txt'
    
class RequiresSystemAndUserAttack(PromptAttack):
    '''
    Attacks that require both system and user prompts (system is just forwarded).
    '''

    @abstractmethod
    def apply(self, system_prompt: str, user_prompt: str) -> Dict[str, str]:
        pass

class RequiresUserOnlyAttack(PromptAttack):
    '''
    Attacks that require only the user prompt (system is generated internally).
    '''
    
    @abstractmethod
    def apply(self, user_prompt: str) -> Dict[str, str]:
        pass

class AssignedPromptAttack(PromptAttack):
    '''Attacks that do not require any input prompts and always return a fixed prompt.'''

    @abstractmethod
    def apply(self) -> Dict[str, str]:
        pass