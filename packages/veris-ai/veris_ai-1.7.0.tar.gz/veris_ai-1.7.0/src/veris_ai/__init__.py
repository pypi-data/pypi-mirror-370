"""Veris AI Python SDK."""

__version__ = "0.1.0"

# Import lightweight modules that only use base dependencies
from .jaeger_interface import JaegerClient
from .models import ResponseExpectation
from .tool_mock import veris
from .observability import init_observability, instrument_fastapi_app

__all__ = [
    "veris",
    "JaegerClient",
    "ResponseExpectation",
    "init_observability",
    "instrument_fastapi_app",
]
