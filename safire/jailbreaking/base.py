import abc

class PromptAttack(abc.ABC):
    '''
    Abstract class for attack
    '''

    @abc.abstractmethod
    def apply(self, user_prompt: str) -> str:
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    def get_filename_template(self) -> str:
        return self.get_name() + '.txt'