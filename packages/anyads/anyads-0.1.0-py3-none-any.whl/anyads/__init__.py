# src/anyads/__init__.py

from .client import PollingSDK, init
from .exceptions import AnyAdsException, InitializationError, APIError

from . import integrations

__all__ = [
    "PollingSDK",
    "init",
    "AnyAdsException",
    "InitializationError",
    "APIError",
    "integrations",
]

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())