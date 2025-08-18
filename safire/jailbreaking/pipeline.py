from safire.jailbreaking.base import PromptAttack

class AttackPipeline:
    '''
    Class for sequentially applying a set of attacks

    Parameters:
        attacks (List[PromptAttack]):
            List of attacks to be applied sequentially

    Methods:
        __call__(prompts: List[str]) -> List[str]:
            Applies the pipeline to a list of prompts
    '''

    def __init__(self, attacks: list[PromptAttack]):
        self.attacks = attacks

    def __call__(self, prompts: list[str]) -> list[str]:
        results = []

        for prompt in prompts:
            for attack in self.attacks:
                prompt = attack.apply(prompt)

            results.append(prompt)

        return results