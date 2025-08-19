"""Logging utilities for VERIS tool calls and responses."""

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def log_tool_call_async(
    session_id: str,
    function_name: str,
    parameters: dict[str, Any],
    docstring: str,
) -> None:
    """Log tool call asynchronously to the VERIS logging endpoint."""
    base_url = os.getenv("VERIS_ENDPOINT_URL")
    if not base_url:
        logger.warning("VERIS_ENDPOINT_URL not set, skipping tool call logging")
        return
    base_url = base_url.rstrip("/")

    endpoint = f"{base_url}/api/v2/simulations/{session_id}/log_tool_call"
    payload = {
        "function_name": function_name,
        "parameters": parameters,
        "docstring": docstring,
    }

    timeout = float(os.getenv("VERIS_MOCK_TIMEOUT", "90.0"))

    try:
        headers: dict[str, str] | None = None
        try:
            from opentelemetry.propagate import get_global_textmap

            headers = {}
            get_global_textmap().inject(headers)
        except Exception:  # pragma: no cover - otel optional
            headers = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            logger.debug(f"Tool call logged for {function_name}")
    except Exception as e:
        logger.warning(f"Failed to log tool call for {function_name}: {e}")


def log_tool_call_sync(
    session_id: str,
    function_name: str,
    parameters: dict[str, Any],
    docstring: str,
) -> None:
    """Log tool call synchronously to the VERIS logging endpoint."""
    base_url = os.getenv("VERIS_ENDPOINT_URL")
    if not base_url:
        logger.warning("VERIS_ENDPOINT_URL not set, skipping tool call logging")
        return

    endpoint = f"{base_url}/api/v2/simulations/{session_id}/log_tool_call"
    payload = {
        "function_name": function_name,
        "parameters": parameters,
        "docstring": docstring,
    }

    timeout = float(os.getenv("VERIS_MOCK_TIMEOUT", "90.0"))

    try:
        headers: dict[str, str] | None = None
        try:
            from opentelemetry.propagate import get_global_textmap  # type: ignore[import-not-found]

            headers = {}
            get_global_textmap().inject(headers)
        except Exception:  # pragma: no cover - otel optional
            headers = None

        with httpx.Client(timeout=timeout) as client:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            logger.debug(f"Tool call logged for {function_name}")
    except Exception as e:
        logger.warning(f"Failed to log tool call for {function_name}: {e}")


async def log_tool_response_async(session_id: str, response: Any) -> None:  # noqa: ANN401
    """Log tool response asynchronously to the VERIS logging endpoint."""
    base_url = os.getenv("VERIS_ENDPOINT_URL")
    if not base_url:
        logger.warning("VERIS_ENDPOINT_URL not set, skipping tool response logging")
        return

    endpoint = f"{base_url}/api/v2/simulations/{session_id}/log_tool_response"
    payload = {
        "response": json.dumps(response, default=str),
    }

    timeout = float(os.getenv("VERIS_MOCK_TIMEOUT", "90.0"))

    try:
        headers: dict[str, str] | None = None
        try:
            from opentelemetry.propagate import get_global_textmap  # type: ignore[import-not-found]

            headers = {}
            get_global_textmap().inject(headers)
        except Exception:  # pragma: no cover - otel optional
            headers = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            http_response = await client.post(endpoint, json=payload, headers=headers)
            http_response.raise_for_status()
            logger.debug("Tool response logged")
    except Exception as e:
        logger.warning(f"Failed to log tool response: {e}")


def log_tool_response_sync(session_id: str, response: Any) -> None:  # noqa: ANN401
    """Log tool response synchronously to the VERIS logging endpoint."""
    base_url = os.getenv("VERIS_ENDPOINT_URL")
    if not base_url:
        logger.warning("VERIS_ENDPOINT_URL not set, skipping tool response logging")
        return

    endpoint = f"{base_url}/api/v2/simulations/{session_id}/log_tool_response"
    payload = {
        "response": json.dumps(response, default=str),
    }

    timeout = float(os.getenv("VERIS_MOCK_TIMEOUT", "90.0"))

    try:
        headers: dict[str, str] | None = None
        try:
            from opentelemetry.propagate import get_global_textmap  # type: ignore[import-not-found]

            headers = {}
            get_global_textmap().inject(headers)
        except Exception:  # pragma: no cover - otel optional
            headers = None

        with httpx.Client(timeout=timeout) as client:
            http_response = client.post(endpoint, json=payload, headers=headers)
            http_response.raise_for_status()
            logger.debug("Tool response logged")
    except Exception as e:
        logger.warning(f"Failed to log tool response: {e}")
