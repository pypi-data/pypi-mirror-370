from importlib.metadata import version

from . import utils
from .api import EazyrentSDK

__version__ = version("eazyrent")

__all__ = ["EazyrentSDK", "utils"]
