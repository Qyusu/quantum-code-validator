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

### 1. Install with uv

```bash
git clone https://github.com/yourusername/quantum-code-validator.git
cd quantum-code-validator
```

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies using uv:
   ```bash
   uv sync
   ```

4. Run the server:
   ```bash
   uv run src/server.py
   ```

---

### 2. Install with Docker

1. Set the required environment variables (for downloading reference documents from Google Cloud Storage):
   - `GOOGLE_CREDENTIALS_JSON`: Service account JSON string
   - `GCS_BUCKET_NAME`: GCS bucket name
   - `GCS_PREFIX`: (Optional) Prefix within the bucket

2. Build and run the container:
   ```bash
   docker build -t quantum-code-validator .
   docker run -p 8000:8000 \
     -e GOOGLE_CREDENTIALS_JSON='...' \
     -e GCS_BUCKET_NAME='your-bucket' \
     -e GCS_PREFIX='your/prefix' \
     quantum-code-validator
   ```

   *You can pass `GOOGLE_CREDENTIALS_JSON` directly as a string or use a `.env` file with the `--env-file` option.*

3. The server will start on port 8000 by default.

## Setting MCP Server
### 1. Local MCP Server by uv 
```json
{
  "mcpServers": {
      "quantum-code-validator": {
          "command": "uv",
          "args": [
              "--directory",
              "/your/mcp/server/directory/quantum-code-validator",
              "run",
              "server.py",
              "--transport",
              "stdio"
          ]
      }
  }
}
```

### 2. Local MCP Server by Docker
```json
{
  "mcpServers": {
      "quantum-code-validator": {
          "command": "docker",
          "args": [
              "run",
              "-p",
              "8000:8000",
              "-e",
              "GOOGLE_CREDENTIALS_JSON=...",
              "-e",
              "GCS_BUCKET_NAME=your-bucket",
              "-e",
              "GCS_PREFIX=your/prefix",
              "-e",
              "TRANSPORT=stdio"
              "quantum-code-validator"
          ]
      }
  }
}
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
