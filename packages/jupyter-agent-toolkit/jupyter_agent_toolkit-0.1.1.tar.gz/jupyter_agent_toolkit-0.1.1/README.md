# Jupyter Agent Toolkit

A Python toolkit for building agent tools and servers that interact with Jupyter kernels and the Jupyter protocol. This package provides high-level wrappers and abstractions around [jupyter_client](https://pypi.org/project/jupyter-client/), making it easy to manage kernels, execute code, and build agent-driven workflows for automation, orchestration, and integration with Model Context Protocol (MCP) servers.

## Features
- High-level, async-friendly wrappers for Jupyter kernel management and code execution
- Session and variable management for agent tools
- Designed for use in agent toolkits, automation, and MCP server backends
- Extensible hooks and integration points for custom workflows

## Use Cases
- Build agent tools that execute code in Jupyter kernels
- Integrate Jupyter kernel execution into MCP servers or other orchestration systems
- Automate notebook and code execution for data science, ML, and automation pipelines

## Installation

You can install the package and its dependencies from PyPI or set up a development environment using pip or [uv](https://github.com/astral-sh/uv).

### Install from PyPI

```sh
# Using pip
pip install jupyter-agent-toolkit

# Or using uv
uv pip install jupyter-agent-toolkit
```

### Environment Setup

### Development Environment (contributors)

#### Option 1: Using pip

```sh
# Create a virtual environment (Python 3.10+ recommended)
python3 -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install the package in editable mode with dev dependencies
pip install -e '.[dev]'
```

#### Option 2: Using uv

```sh
# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install the package in editable mode with dev dependencies
uv pip install '.[dev]'
```

## Configuration

- All configuration is managed via `pyproject.toml`.
- Development dependencies and test tools are specified in the `[project.optional-dependencies]` section.
- See `tox.ini` for test and linting environments.

## Reference: jupyter_client

[jupyter_client](https://pypi.org/project/jupyter-client/) is the reference implementation of the Jupyter protocol, providing client and kernel management APIs. This toolkit builds on top of jupyter_client to provide a more ergonomic, agent-oriented interface for automation and integration.

## Project Goals

- Define reusable components and abstractions for agent tools that interact with Jupyter kernels
- Enable both direct use in agent toolkits and integration as part of an MCP server
- Provide a robust, modern, and extensible foundation for agent-driven Jupyter workflows

## Development

- See the `tests/` directory for usage examples and test coverage.
- Contributions and feedback are welcome!