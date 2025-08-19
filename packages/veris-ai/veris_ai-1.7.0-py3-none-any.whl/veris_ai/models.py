"""Models for the VERIS SDK."""

from enum import Enum


class ResponseExpectation(str, Enum):
    """Expected response behavior for tool mocking."""

    AUTO = "auto"
    REQUIRED = "required"
    NONE = "none"
