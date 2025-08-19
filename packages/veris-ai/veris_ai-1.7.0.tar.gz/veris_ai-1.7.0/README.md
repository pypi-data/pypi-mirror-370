# Veris AI Python SDK

A Python package for Veris AI tools with simulation capabilities and FastAPI MCP (Model Context Protocol) integration.

## Quick Reference

**Purpose**: Tool mocking, tracing, and FastAPI MCP integration for AI agent development  
**Core Components**: [`tool_mock`](#function-mocking) • [`observability`](#sdk-observability-helpers) • [`fastapi_mcp`](#fastapi-mcp-integration) • [`jaeger_interface`](#jaeger-trace-interface)  
**Deep Dive**: [`Module Architecture`](src/veris_ai/README.md) • [`Testing Guide`](tests/README.md) • [`Usage Examples`](examples/README.md)  
**Source of Truth**: Implementation details in [`src/veris_ai/`](src/veris_ai/) source code

## Installation

```bash
# Base package
uv add veris-ai

# With optional extras
uv add "veris-ai[dev,fastapi,instrument]"
```

**Installation Profiles**:
- `dev`: Development tools (ruff, pytest, mypy) 
- `fastapi`: FastAPI MCP integration
- `observability`: OpenTelemetry tracing

## Import Patterns

**Semantic Tag**: `import-patterns`

```python
# Core imports (base dependencies only)
from veris_ai import veris, JaegerClient

# Optional features (require extras)
from veris_ai import init_observability, instrument_fastapi_app  # Provided by SDK observability helpers
```

**Complete Import Strategies**: See [`examples/README.md`](examples/README.md) for five different import approaches, conditional features, and integration patterns.

## Configuration

**Semantic Tag**: `environment-config`

| Variable | Purpose | Default |
|----------|---------|---------|
| `VERIS_ENDPOINT_URL` | Mock server endpoint | *Required* |
| `VERIS_MOCK_TIMEOUT` | Request timeout (seconds) | `90.0` |
| `ENV` | Set to `"simulation"` for mock mode | Production |
| `VERIS_SERVICE_NAME` | Tracing service name | Auto-detected |
| `VERIS_OTLP_ENDPOINT` | OpenTelemetry collector | *Required for tracing* |

**Configuration Details**: See [`src/veris_ai/tool_mock.py`](src/veris_ai/tool_mock.py) for environment handling logic.


### SDK Observability Helpers

The SDK provides optional-safe observability helpers that standardize OpenTelemetry setup and W3C context propagation across services.

```python
from fastapi import FastAPI
from veris_ai import init_observability, instrument_fastapi_app

# Initialize tracing/export early (no-op if dependencies are absent)
init_observability(service_name="my-customer-service")

app = FastAPI()

# Ensure inbound HTTP requests continue W3C traces
instrument_fastapi_app(app)
```

What this enables:
- Sets global W3C propagator (TraceContext + Baggage)
- Optionally instruments FastAPI, requests, httpx, MCP client if installed
- Includes request hooks to attach outbound `traceparent` on HTTP calls for continuity

End-to-end propagation with the simulator:
- The simulator injects W3C headers when connecting to your FastAPI MCP endpoints
- The SDK injects W3C headers on `/api/v2/tool_mock` and logging requests back to the simulator
- Result: customer agent spans and tool mocks appear under the same distributed trace

## Function Mocking

**Semantic Tag**: `tool-mocking`

### Core Decorators

```python
from veris_ai import veris

# Mock mode: Returns simulated responses in ENV=simulation
@veris.mock()
async def your_function(param1: str, param2: int) -> dict:
    """Function documentation for LLM context."""
    return {"result": "actual implementation"}

# Spy mode: Executes function but logs calls/responses
@veris.mock(mode="spy")
async def monitored_function(data: str) -> dict:
    return process_data(data)

# Stub mode: Returns fixed value in simulation
@veris.stub(return_value={"status": "success"})
async def get_data() -> dict:
    return await fetch_from_api()
```

**Behavior**: In simulation mode, decorators intercept calls to mock endpoints. In production, functions execute normally.

**Implementation**: See [`src/veris_ai/tool_mock.py`](src/veris_ai/tool_mock.py) for decorator logic and API integration.

## FastAPI MCP Integration

**Semantic Tag**: `fastapi-mcp`

Expose FastAPI endpoints as MCP tools for AI agent consumption using HTTP transport.

```python
from fastapi import FastAPI
from veris_ai import veris

app = FastAPI()

# Enable MCP integration with HTTP transport
veris.set_fastapi_mcp(
    fastapi=app,
    name="My API Server",
    include_operations=["get_users", "create_user"],
    exclude_tags=["internal"]
)

# Mount the MCP server with HTTP transport (recommended)
veris.fastapi_mcp.mount_http()
```

**Key Features**:
- **HTTP Transport**: Uses Streamable HTTP protocol for better session management
- **Automatic schema conversion**: FastAPI OpenAPI → MCP tool definitions
- **Session management**: Bearer token → session ID mapping
- **Filtering**: Include/exclude operations and tags
- **Authentication**: OAuth2 integration

**Transport Protocol**: The SDK uses HTTP transport (via `mount_http()`) which implements the MCP Streamable HTTP specification, providing robust connection handling and fixing session routing issues with concurrent connections.

**Configuration Reference**: See function signature in [`src/veris_ai/tool_mock.py`](src/veris_ai/tool_mock.py) for all `set_fastapi_mcp()` parameters.

## Utility Functions

**Semantic Tag**: `json-schema-utils`

```python
from veris_ai.utils import extract_json_schema

# Schema extraction from types
user_schema = extract_json_schema(User)  # Pydantic models
list_schema = extract_json_schema(List[str])  # Generics
```

**Supported Types**: Built-in types, generics (List, Dict, Union), Pydantic models, TypedDict, forward references.

**Implementation**: See [`src/veris_ai/utils.py`](src/veris_ai/utils.py) for type conversion logic.

## Development

**Semantic Tag**: `development-setup`

**Requirements**: Python 3.11+, `uv` package manager

```bash
# Install with dev dependencies
uv add "veris-ai[dev]"

# Quality checks
ruff check --fix .    # Lint and format
pytest --cov=veris_ai # Test with coverage
```

**Testing & Architecture**: See [`tests/README.md`](tests/README.md) for test structure, fixtures, and coverage strategies. See [`src/veris_ai/README.md`](src/veris_ai/README.md) for module architecture and implementation flows.

## Module Architecture

**Semantic Tag**: `module-architecture`

**Core Modules**: `tool_mock` (mocking), `jaeger_interface` (trace queries), `utils` (schema conversion)

**Complete Architecture**: See [`src/veris_ai/README.md`](src/veris_ai/README.md) for module overview, implementation flows, and configuration details. 

## Jaeger Trace Interface

**Semantic Tag**: `jaeger-query-api`

```python
from veris_ai.jaeger_interface import JaegerClient

client = JaegerClient("http://localhost:16686")
traces = client.search(service="veris-agent", tags={"error": "true"})
```

**Complete Guide**: See [`src/veris_ai/jaeger_interface/README.md`](src/veris_ai/jaeger_interface/README.md) for API reference, filtering strategies, and architecture details.

---

**License**: MIT License - see [LICENSE](LICENSE) file for details. 