from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from src.tools import request_pennylane_reference, validate_pennylane_code_statically

mcp = FastMCP(
    name="QuantumCodeValidator",
    instructions="""
    Provides a set of tools for statically validating Python code that uses the quantum computing library PennyLane.
    This service checks the correctness and usage of PennyLane methods by comparing the code against the official
    documentation for a specified version. Additionally, it offers functionality to retrieve reference documentation
    for individual PennyLane methods, supporting quantum algorithm developers in writing accurate and up-to-date code.
    """,
    dependencies=["ast", "py_compile", "pennylane"],
    log_level="DEBUG",
)


@mcp.tool(
    description="""Static validation of code containing PennyLane methods.
    PennyLane is a Python library for quantum computing.

    This tool statically validates a PennyLane code by following steps:
    1. Check the syntax of the code by ast module.
    2. Check the compilation of the code by py_compile module.
    3. Check the usage of PennyLane library methods by comparing with the document of the specific version.

    The version is optional. If not specified, version set to None.
    Current supported versions are v0.35.0, v0.35.1, v0.36.0, v0.37.0, v0.38.0,
    v0.38.1, v0.39.0, v0.40.0, v0.41.0, v0.41.1.
    """
)
def validate_pennylane_method_by_static(
    code: Annotated[str, Field(description="source code that includes PennyLane methods.")],
    version: Annotated[
        str | None, Field(None, description="The version of the PennyLane library to use. (ex: 'v0.41.1')")
    ],
) -> dict:
    """Static validation of code containing PennyLane methods."""
    return validate_pennylane_code_statically(code, version)


@mcp.tool(
    description="""Request reference documentation of a method in a specific version of the PennyLane library.
    The PennyLane library is a Python library for quantum computing.

    This tool requests reference documentation for a specific version of the PennyLane library.
    The method name only includes the method name and the module name.
    Do not include parentheses and arguments. (ex: "qml.CNOT(wires=[0, 1])" -> "qml.CNOT")
    The version is optional. If not specified, version set to None.

    Current supported versions are v0.35.0, v0.35.1, v0.36.0, v0.37.0, v0.38.0,
    v0.38.1, v0.39.0, v0.40.0, v0.41.0, v0.41.1.
    """,
)
def request_pennylane_method_reference(
    method_name: Annotated[
        str, Field(description="The name of the PennyLane method to request reference documentation. (ex: 'qml.CNOT')")
    ],
    version: Annotated[
        str | None, Field(None, description="The version of the PennyLane library to use. (ex: 'v0.41.1')")
    ],
) -> str:
    """Request reference documentation of a method in a specific version of the PennyLane library."""
    return request_pennylane_reference(method_name, version)


@mcp.custom_route("/healthz", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Quantum Code Validator MCP Server")


if __name__ == "__main__":
    mcp.run(transport="sse")
