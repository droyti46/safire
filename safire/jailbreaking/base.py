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

import os
from typing import Dict, Literal, Optional
from abc import ABC, abstractmethod

from safire.utils import camel_to_snake

__all__ = [
    'RequiresSystemAndUserAttack',
    'RequiresUserOnlyAttack',
    'RequiresSystemOnlyAttack',
    'AssignedPromptAttack'
]

# --- Custom name decorator ---

def with_custom_name(custom_name: Optional[str] = None):
    '''
    Class decorator that automatically sets a custom name for attack classes.
    
    Args:
        custom_name (str, optional):
            The custom name to assign to the attack class. If None,
            the class will use its default name conversion.
    
    Returns:
        A decorated class with the custom name preset.
    '''
    def decorator(cls):
        # Store the original __init__ method
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # If custom_name was provided to the decorator, set it
            if custom_name is not None:
                kwargs['custom_name'] = custom_name
            # Call the base class __init__
            super(cls, self).__init__(*args, **kwargs)
            # Call the original __init__ of the derived class if it exists
            if original_init is not object.__init__:
                original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        return cls
    
    return decorator

# --- Base class ---

class PromptAttack(ABC):
    '''
    Abstract class for attack
    '''

    def __init__(self, custom_name: Optional[str] = None):
        self._custom_name = custom_name

    def get_name(self) -> str:
        '''
        Returns the name of the attack.

        Returns:
            str: The attack identifier.
        '''
        if self._custom_name is not None:
            return self._custom_name
        
        return camel_to_snake(self.__class__.__name__)

    def get_filename_template(self, role: Literal['user', 'system']) -> str:
        '''
        Returns the template filename of the attack.

        Args:
            role (str): The template role ('user' or 'system')

        Returns:
            str: The attack template filename.
        '''
        if role not in ('user', 'system'):
            raise ValueError(f'Role must be "user" or "system", got "{role}"')
        
        return os.path.join(role, self.get_name() + '.txt')

# --- Template attack classes ---

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

# --- Assigned attack classes ---

class RequiresSystemOnlyAttack(PromptAttack):
    '''
    Attacks that require only the system prompt (user is fixed).
    '''
    
    @abstractmethod
    def apply(self, system_prompt: str) -> Dict[str, str]:
        pass

class AssignedPromptAttack(PromptAttack):
    '''Attacks that do not require any input prompts and always return a fixed prompt.'''

    @abstractmethod
    def apply(self) -> Dict[str, str]:
        pass