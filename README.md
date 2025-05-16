# Quantum Code Validator

A Model Context Protocol (MCP) server for validating quantum computing library code. Currently supports PennyLane, with plans to expand support for other quantum computing libraries in the future.

## Overview

The Quantum Code Validator is a tool that helps developers ensure their quantum computing code is valid and follows the correct usage patterns for various quantum libraries. It provides static validation of quantum code against official documentation and offers reference documentation lookup capabilities.

## Features

- **Static Code Validation**: Validates quantum code by:
  - Checking code syntax using Python's `ast` module
  - Verifying code compilation using `py_compile`
  - Comparing quantum library method usage against official documentation
- **Reference Documentation Lookup**: Retrieves method documentation for specific versions of quantum libraries
- **Version-Specific Validation**: Supports validation against specific versions of quantum libraries
- **Extensible Architecture**: Designed to support multiple quantum computing libraries

## Current Support

- **PennyLane**: Full support for static validation and reference documentation lookup
  - Supported versions: v0.35.0 - v0.41.1

## Planned Support

The following quantum computing libraries are planned for future support:
- Qulacs
- Qiskit
- Cirq
- cuQuantum
- And more...

## Usage

The server provides two main tools:

1. `validate_quantum_method_by_static`:
   ```python
   # Example usage
   result = validate_quantum_method_by_static(
       code="your_quantum_code_here",
       version="v0.41.1"  # Optional
   )
   ```

2. `request_quantum_method_reference`:
   ```python
   # Example usage
   docs = request_quantum_method_reference(
       method_name="qml.CNOT",  # Method name without arguments
       version="v0.41.1"  # Optional
   )
   ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quantum-code-validator.git
   cd quantum-code-validator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Development

The project uses Python's modern tooling:
- `pyproject.toml` for project configuration
- `uv` for dependency management
- FastMCP for the server implementation


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
