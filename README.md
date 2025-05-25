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

<!--
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
-->

## Setting MCP Server
### 1. Local MCP Server by uv 
1.1 Load and Parse PennyLane Source Code
Load basic information from PennyLane's source code and save it as JSON files by version. The PennyLane version will be the one installed in the execution environment, so please switch it using the uv command as needed.
```bash
uv run scripts/parse_pennylane_api.py ./refdocs/pennylane/raw/v0.41.1.json
```

1.2 Format Source Code to Document
Next, we will use an LLM to format the basic information extracted in Step 1 into document information that can be accessed on MCP. Please specify the PennyLane versions to be converted into documents as a comma-separated list. Note that this process uses an LLM, so the "OPENAI_API_KEY" environment variable must be set, and there is a cost of approximately $2.50 per version. The formatting results will be saved in `"./refdocs/pennylane/formatted"`.
```bash
uv run scripts/format_docs_by_llm.py v0.41.0,v0.41.1
```

1.3 Setup MCP Server on Local
Finally, by configuring the `mcp.json` file according to the platform and starting the MCP server, the tool becomes available for use with the target tool. As a reference, a [link](https://modelcontextprotocol.io/quickstart/server#testing-your-server-with-claude-for-desktop) to the documentation on how to configure it for Claude Desktop is provided.
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

### 2. Use Remote Server
Although Claude Desktop does not support MCP servers launched remotely, tools such as Cline or Cursor can connect to MCP via a remote server using the following configuration.
```json
{
  "mcpServers": {
      "quantum-code-validator": {
        "url": "https://quantum-code-validator.onrender.com/sse"
      }
  }
}
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
