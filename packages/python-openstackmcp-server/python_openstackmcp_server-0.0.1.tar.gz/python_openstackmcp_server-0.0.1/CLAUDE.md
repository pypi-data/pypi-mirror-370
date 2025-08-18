**# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync --all-groups`
- **Install pre-commit hooks**: `pre-commit install`

### Testing
- **Run all tests**: `uv run pytest`
- **Run specific test file**: `uv run pytest tests/tools/test_compute_tools.py`
- **Run tests with coverage**: `uv run pytest --cov=src/openstack_mcp_server`

### Code Quality
- **Format and lint**: `uv run ruff format . && uv run ruff check .`
- **Check formatting only**: `uv run ruff format --check .`
- **Lint only**: `uv run ruff check .`
- **Fix linting issues**: `uv run ruff check --fix .`

### Running the Server
- **Run MCP server**: `uv run python -m openstack_mcp_server`
- **Run with specific transport**: `TRANSPORT=sse uv run python -m openstack_mcp_server`

## Architecture Overview

### Core Components

**MCP Server Framework**: Built on FastMCP with middleware for error handling and logging. The server supports multiple transport protocols (stdio, sse, streamable-http) configured via environment variables.

**OpenStack Integration**: Uses OpenStack SDK with a singleton connection manager pattern in `tools/base.py`. Connection is established using cloud configuration from `clouds.yaml`.

**Tool Organization**: OpenStack services are organized into tool classes:
- `ComputeTools`: Server management (list, get, create) and flavor operations
- `ImageTools`: Image service operations  
- `IdentityTools`: Authentication and identity management
- `NetworkTools`: Network resource management
- `BlockStorageTools`: Volume and storage operations

**Response Models**: Pydantic models in `tools/response/` define structured responses for each service, handling OpenStack SDK field mapping and validation.

### Key Patterns

**Tool Registration**: Each tool class implements `register_tools(mcp)` method that registers individual methods as MCP tools using decorators.

**Connection Management**: Single OpenStack connection instance managed through `OpenStackConnectionManager` class with lazy initialization.

**Configuration**: Environment-based configuration in `config.py` for transport protocol, cloud name, and debug settings.

**Error Handling**: Middleware-based error handling with structured logging to stderr.

## Environment Configuration

Required environment variables:
- `CLOUD_NAME`: OpenStack cloud configuration name (default: "openstack")
- `TRANSPORT`: MCP transport protocol (default: "stdio")
- `DEBUG_MODE`: Enable OpenStack SDK debug logging (default: "true")

OpenStack credentials configured via `clouds.yaml` file in project root.

## Branch Strategy

- Main development on `develop` branch
- PRs to `main` restricted to `develop` branch merges
- Requires 2 code reviewer approvals for develop branch merges
- Uses Conventional Commits format for commit messages**