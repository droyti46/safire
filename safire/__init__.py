import importlib

__all__ = ['jailbreaking', 'evaluation']

def __getattr__(name):
    if name in __all__:
        return importlib.import_module(f'{__name__}.{name}')
    raise AttributeError(f'module {__name__} has no attribute {name}')
