from typing import Optional

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from tools import request_pennylane_reference, validate_pennylane_code_statically

mcp = FastMCP(name="QuantumCodeValidator", stateless_http=True, json_response=True, log_level="DEBUG")


@mcp.tool(
    description="""Static validation of code containing PennyLane methods
    against the documentation of the target version."""
)
def validate_pennylane_method_by_static(code: str, version: Optional[str] = None) -> dict:
    """Static validation of code containing PennyLane methods. PennyLane is a Python library for quantum computing.

    This tool statically validates a PennyLane code by following steps:
    1. Check the syntax of the code by ast module.
    2. Check the compilation of the code by py_compile module.
    3. Check the usage of PennyLane library methods by comparing with the document of the specific version.

    The version is optional. If not specified, version set to None.

    Args:
        code (str): source code that includes PennyLane methods.
        version (Optional[str]): The version of the PennyLane library to use. (ex: "v0.41.1")

    Returns:
        dict: A dictionary containing the validation results.
    """
    return validate_pennylane_code_statically(code, version)


@mcp.tool(
    description="Request for the reference documentation of a method in a specific version of the PennyLane library."
)
def request_pennylane_method_reference(method_name: str, version: Optional[str] = None) -> str:
    """Request reference documentation of a method in a specific version of the PennyLane library.
    The PennyLane library is a Python library for quantum computing.

    This tool requests reference documentation for a specific version of the PennyLane library.
    The method name only includes the method name and the module name.
    Do not include parentheses and arguments. (ex: "qml.CNOT(wires=[0, 1])" -> "qml.CNOT")
    The version is optional. If not specified, version set to None.

    Args:
        method_name (str): The name of the PennyLane method to request reference documentation. (ex: "qml.CNOT")
        version (Optional[str]): The version of the PennyLane library to use. (ex: "v0.41.1")

    Returns:
        str: The reference documentation for the specified PennyLane method.
    """
    return request_pennylane_reference(method_name, version)


@mcp.custom_route("/healthz", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Quantum Code Validator MCP Server")


@mcp.custom_route("/tools", methods=["GET"])
async def list_tools(request: Request) -> JSONResponse:
    tools = [
        {
            "name": "validate_pennylane_method_by_static",
            "description": "Static validation of code containing PennyLane methods against the documentation of the target version.",
        },
        {
            "name": "request_pennylane_method_reference",
            "description": "Request for the reference documentation of a method in a specific version of the PennyLane library.",
        },
    ]
    return JSONResponse({"tools": tools})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
