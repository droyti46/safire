import importlib
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('safire-py')
except PackageNotFoundError:
    __version__ = '0.0.0'

__all__ = ['jailbreaking', 'evaluation']

def __getattr__(name):
    if name in __all__:
        return importlib.import_module(f'{__name__}.{name}')
    raise AttributeError(f'module {__name__} has no attribute {name}')
