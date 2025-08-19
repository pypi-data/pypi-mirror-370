import asyncio
import os
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from veris_ai import veris
from veris_ai.tool_mock import _session_id_context


@pytest.fixture
def tool_mock():
    return veris


# Test mock decorator
@pytest.mark.asyncio
async def test_mock_decorator_simulation_mode(simulation_env):
    @veris.mock(mode="function")
    async def test_func(param1: str, param2: int) -> dict[str, Any]:
        return {"result": "real"}

    mock_response = {"result": {"mocked": True}}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func("test", 42)
        assert result == {"result": {"mocked": True}}


@pytest.mark.asyncio
async def test_mock_decorator_production_mode(production_env):
    @veris.mock(mode="function")
    async def test_func(param1: str, param2: int) -> dict:
        return {"result": "real"}

    result = await test_func("test", 42)
    assert result == {"result": "real"}


@pytest.mark.asyncio
async def test_mock_with_context(simulation_env):
    @veris.mock(mode="function")
    async def test_func() -> dict:
        return {"result": "real"}

    mock_response = {"result": {"mocked": True}}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )
        veris.set_session_id("test-session-id")
        result = await test_func()
        first_call = mock_client.return_value.__aenter__.return_value.post.call_args
        assert first_call.kwargs["json"]["session_id"] == "test-session-id"
        assert result == {"result": {"mocked": True}}


@pytest.mark.asyncio
async def test_mock_without_context():
    """Test that without session_id, the function runs in production mode."""

    @veris.mock(mode="function")
    async def test_func() -> dict:
        return {"result": "real"}

    # Clear session_id to ensure production mode
    veris.clear_session_id()

    # In production mode, the original function should be called
    result = await test_func()
    assert result == {"result": "real"}


# Test error handling
@pytest.mark.asyncio
async def test_mock_http_error(simulation_env):
    @veris.mock(mode="function")
    async def test_func(param1: str) -> dict:
        return {"result": "real"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.HTTPError("Mock HTTP Error"),
        )

        with pytest.raises(httpx.HTTPError):
            await test_func("test")


@pytest.mark.asyncio
async def test_mock_missing_endpoint():
    """Test that missing endpoint raises ValueError when function is called in simulation mode."""
    with patch.dict(os.environ, {"VERIS_ENDPOINT_URL": ""}):

        @veris.mock()
        async def test_func():
            return {"result": "real"}

        # Set session_id to enable simulation mode
        veris.set_session_id("test-session")

        # Error should be raised when function is called
        with pytest.raises(ValueError, match="VERIS_ENDPOINT_URL environment variable is not set"):
            await test_func()


@pytest.mark.asyncio
async def test_mock_invalid_endpoint(simulation_env):
    with patch.dict(os.environ, {"VERIS_ENDPOINT_URL": ""}), pytest.raises(ValueError):

        @veris.mock()
        async def test_func():
            return {"result": "real"}

        await test_func()


@pytest.mark.asyncio
async def test_mock_string_json_response(simulation_env):
    @veris.mock(mode="function")
    async def test_func() -> dict:
        return {"result": "real"}

    mock_response = {"result": '{"key": "value"}'}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func()
        assert result == {"result": '{"key": "value"}'}


# Test context vars behavior
@pytest.mark.asyncio
async def test_context_var_isolation():
    """Test that session_id context vars are isolated between concurrent calls."""

    async def set_and_check_session(session_id: str):
        veris.set_session_id(session_id)
        # Verify the session_id is set correctly
        assert veris.session_id == session_id
        # Simulate some async work
        await asyncio.sleep(0.01)
        # Verify the session_id hasn't changed
        assert veris.session_id == session_id
        return session_id

    # Run multiple concurrent tasks with different session IDs
    tasks = [
        set_and_check_session("session-1"),
        set_and_check_session("session-2"),
        set_and_check_session("session-3"),
    ]

    results = await asyncio.gather(*tasks)
    assert results == ["session-1", "session-2", "session-3"]


@pytest.mark.asyncio
async def test_context_var_persistence_in_call(simulation_env):
    """Test that session_id persists throughout a mock function call."""
    captured_session_ids = []

    @veris.mock(mode="function")
    async def test_func() -> dict:
        # Capture session_id inside the function
        captured_session_ids.append(veris.session_id)
        return {"result": "real"}

    mock_response = {"result": {"mocked": True}}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        async def mock_post(*args, **kwargs):
            # Capture session_id during HTTP call
            captured_session_ids.append(veris.session_id)
            return mock_response_obj

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=mock_post)

        # Set session_id and call function
        veris.set_session_id("test-session-123")
        await test_func()

        # Verify session_id was captured
        # In simulation mode, we should have 2 captures (one in function, one in HTTP call)
        # But if the function ran in production mode, we'd only have 1
        assert len(captured_session_ids) >= 1
        assert captured_session_ids[0] == "test-session-123"

        # Verify the HTTP client was called with correct session_id
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        assert call_args[1]["json"]["session_id"] == "test-session-123"


@pytest.mark.asyncio
async def test_context_var_cleanup():
    """Test that clearing session_id works correctly."""
    # Set a session_id
    veris.set_session_id("test-session")
    assert veris.session_id == "test-session"

    # Clear it
    veris.clear_session_id()
    assert veris.session_id is None

    # Verify it stays None
    await asyncio.sleep(0.01)
    assert veris.session_id is None


@pytest.mark.asyncio
async def test_context_var_no_interference():
    """Test that context vars don't interfere between different async contexts."""
    results = []

    async def task1():
        veris.set_session_id("task1-session")
        await asyncio.sleep(0.02)
        results.append(("task1", veris.session_id))

    async def task2():
        await asyncio.sleep(0.01)
        # Should be None since we didn't set it in this context
        results.append(("task2", veris.session_id))
        veris.set_session_id("task2-session")
        results.append(("task2-after", veris.session_id))

    await asyncio.gather(task1(), task2())

    # Verify results
    assert ("task1", "task1-session") in results
    assert ("task2", None) in results
    assert ("task2-after", "task2-session") in results


# Test stub decorator
@pytest.mark.asyncio
async def test_stub_decorator_simulation_mode(simulation_env):
    """Test that stub decorator returns stubbed value in simulation mode."""
    stub_value = {"stubbed": True, "data": "test_data"}

    @veris.stub(return_value=stub_value)
    async def my_function(x: int) -> dict:
        return {"real": True, "value": x}

    result = await my_function(42)
    assert result == stub_value
    assert result["stubbed"] is True
    assert result["data"] == "test_data"


@pytest.mark.asyncio
async def test_stub_decorator_production_mode(production_env):
    """Test that stub decorator executes original function in production mode."""
    stub_value = {"stubbed": True, "data": "test_data"}

    @veris.stub(return_value=stub_value)
    async def my_function(x: int) -> dict:
        return {"real": True, "value": x}

    result = await my_function(42)
    assert result == {"real": True, "value": 42}
    assert result.get("stubbed") is None


@pytest.mark.asyncio
async def test_stub_decorator_with_complex_return_value(simulation_env):
    """Test stub decorator with complex return values."""

    class CustomObject:
        def __init__(self, name: str, values: list[int]):
            self.name = name
            self.values = values

    stub_obj = CustomObject("test", [1, 2, 3])

    @veris.stub(return_value=stub_obj)
    async def get_custom_object() -> CustomObject:
        return CustomObject("real", [4, 5, 6])

    result = await get_custom_object()
    assert isinstance(result, CustomObject)
    assert result.name == "test"
    assert result.values == [1, 2, 3]


@pytest.mark.asyncio
async def test_stub_decorator_preserves_function_metadata(simulation_env):
    """Test that stub decorator preserves function metadata."""
    stub_value = "stubbed"

    @veris.stub(return_value=stub_value)
    async def documented_function(x: int, y: str = "default") -> str:
        """This is a documented function."""
        return f"{x}: {y}"

    # Check function metadata is preserved
    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This is a documented function."

    # Function still works
    result = await documented_function(10)
    assert result == stub_value


@pytest.mark.asyncio
async def test_stub_decorator_with_none_value(simulation_env):
    """Test stub decorator with None as return value."""

    @veris.stub(return_value=None)
    async def returns_none() -> Any:
        return {"should": "not_return_this"}

    result = await returns_none()
    assert result is None


# Test mock decorator with mode parameter
@pytest.mark.asyncio
async def test_mock_decorator_tool_mode(simulation_env):
    """Test mock decorator with mode='tool'."""

    @veris.mock(mode="tool")
    async def test_func() -> dict:
        return {"result": "real"}

    mock_response = {"result": "mocked"}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func()
        assert result == {"result": "mocked"}


@pytest.mark.asyncio
async def test_mock_decorator_function_mode(simulation_env):
    """Test mock decorator with mode='function'."""

    @veris.mock(mode="function")
    async def test_func() -> dict:
        return {"result": "real"}

    mock_response = {"mocked": True, "data": [1, 2, 3]}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func()
        assert result == mock_response


@pytest.mark.asyncio
async def test_mock_decorator_with_expects_response(simulation_env):
    """Test mock decorator with expects_response parameter."""

    @veris.mock(mode="function", expects_response=True)
    async def test_func() -> dict:
        return {"result": "real"}

    mock_response = {"result": {"mocked": True}}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func()
        # Verify the request payload included expects_response
        first_call = mock_client.return_value.__aenter__.return_value.post.call_args
        assert first_call.kwargs["json"]["response_expectation"] == "required"
        assert result == {"result": {"mocked": True}}


@pytest.mark.asyncio
async def test_mock_decorator_with_cache_response(simulation_env):
    """Test mock decorator with cache_response parameter."""

    @veris.mock(mode="function", cache_response=True)
    async def test_func(x: int) -> dict:
        return {"result": x}

    mock_response = {"result": {"cached": True}}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func(42)
        # Verify the request payload included cache_response
        first_call = mock_client.return_value.__aenter__.return_value.post.call_args
        assert first_call.kwargs["json"]["cache_response"] is True
        assert result == {"result": {"cached": True}}


@pytest.mark.asyncio
async def test_mock_decorator_all_parameters(simulation_env):
    """Test mock decorator with all parameters."""

    @veris.mock(mode="function", expects_response=False, cache_response=True)
    async def test_func(name: str, count: int) -> dict:
        return {"name": name, "count": count}

    mock_response = {"status": "mocked", "values": [1, 2, 3]}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        result = await test_func("test", 3)
        # Verify the request payload
        first_call = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = first_call.kwargs["json"]
        assert payload["response_expectation"] == "none"
        assert payload["cache_response"] is True
        assert result == mock_response


@pytest.mark.asyncio
async def test_mock_decorator_function_mode_defaults_expects_response(simulation_env):
    """Test that function mode defaults expects_response to False."""

    @veris.mock(mode="function")
    async def test_func() -> dict:
        return {"result": "real"}

    mock_response = {"result": {"mocked": True}}

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        await test_func()
        # Verify expects_response is False for function mode by default
        first_call = mock_client.return_value.__aenter__.return_value.post.call_args
        assert first_call.kwargs["json"]["response_expectation"] == "none"


@pytest.mark.asyncio
async def test_mock_decorator_json_schema_in_payload(simulation_env):
    """Test that mock decorator includes JSON schema of return type in payload."""
    from typing import List

    @veris.mock()
    async def test_func() -> List[dict]:
        return [{"result": "real"}]

    mock_response = [{"mocked": True}]

    with patch("veris_ai.tool_mock.httpx.AsyncClient") as mock_client:
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response_obj,
        )

        await test_func()
        # Verify the JSON schema was included in the payload
        first_call = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = first_call.kwargs["json"]
        return_type_schema = payload["tool_call"]["return_type"]
        # Should be a JSON string containing schema for List[dict]
        assert isinstance(return_type_schema, str)
        import json

        schema = json.loads(return_type_schema)
        assert schema["type"] == "array"
        assert "items" in schema
