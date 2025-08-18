import abc

class PromptAttack(abc.ABC):
    '''
    Abstract class for attack
    '''

    @abc.abstractmethod
    def apply(self, user_prompt: str):
        pass