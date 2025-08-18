import random
import importlib

def set_seed(seed: int) -> None:
    '''
    Sets and fixes the random seed for all supported libraries

    Parameters:
        seed (int):
            Random seed

    Examples:
        >>> from safire.utils import set_seed
        >>> set_seed(42)
    '''
    random.seed(seed)

def mask_random_words(user_prompt: str, n: int = 1) -> str:
    '''
    Masks n random words in a given sentence by wrapping them in square brackets

    Parameters:
        user_prompt (str):
            Input sentence

        n (int, optional):
            Number of words to mask. Default is 1.

    Returns:
        str:
            Sentence with n randomly chosen words masked in square brackets

    Examples:
        >>> mask_random_words("Hello world", n=1)
        '[Hello] world'
    '''
    words = user_prompt.split()

    if not words:
        return user_prompt

    n = min(n, len(words))
    indices = random.sample(range(len(words)), n)

    for idx in indices:
        words[idx] = f'[{words[idx]}]'

    return ' '.join(words)

def load_jailbreaking_template(name: str) -> str:
    '''
    Loads a text template by name from the templates directory

    Parameters:
        name (str):
            Name of the jailbreaking template file to load

    Returns:
        str:
            Content of the template file as a string

    Examples:
        >>> load_jailbreaking_template("example.txt")
        'This is an example template content'
    '''
    return importlib.resources.files('safire.jailbreaking.templates') \
                              .joinpath(name) \
                              .read_text(encoding='utf-8')