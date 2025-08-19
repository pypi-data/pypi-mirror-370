from . import generate
from . import evaluate
from . import _utils

import importlib.metadata

__version__ = importlib.metadata.version("randomity")

def version():
    return __version__