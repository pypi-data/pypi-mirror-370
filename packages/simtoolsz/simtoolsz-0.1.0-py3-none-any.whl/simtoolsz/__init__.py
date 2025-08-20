import importlib.metadata

import mail

try:
    __version__ = importlib.metadata.version("simtoolsz")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    '__version__', 'mail'
]