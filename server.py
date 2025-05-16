from typing import Optional

from mcp.server.fastmcp import FastMCP

from tools.request_pennylane_reference import request_reference
from tools.static_validation import static_validation

mcp = FastMCP(
    name="QuantumCodeValidator",
)


@mcp.tool(
    description="""Static validation of code containing quantum library methods
    against the documentation of the target version."""
)
def validate_quantum_method_by_static(code: str, version: Optional[str] = None) -> dict:
    """Validate a static quantum code.

    This tool statically validates a quantum code by following steps:
    1. Check the syntax of the code by ast module.
    2. Check the compilation of the code by py_compile module.
    3. Check the usage of quantum library methods by comparing with the document of the specific version.

    The version is optional. If not specified, version set to None.

    Args:
        code (str): source code that includes quantum methods.
        version (Optional[str]): The version of the quantum library to use. (ex: "v0.41.1")

    Returns:
        dict: A dictionary containing the validation results.
    """
    return static_validation(code, version)


@mcp.tool(
    description="Request for the reference documentation of a method in a specific version of the quantum library."
)
def request_quantum_method_reference(method_name: str, version: Optional[str] = None) -> str:
    """Request reference documentation.

    This tool requests reference documentation for a specific version of the quantum library.
    The method name only includes the method name and the module name.
    Do not include parentheses and arguments. (ex: "qml.CNOT(wires=[0, 1])" -> "qml.CNOT")
    The version is optional. If not specified, version set to None.

    Args:
        method_name (str): The name of the quantum method to request reference documentation. (ex: "qml.CNOT")
        version (Optional[str]): The version of the quantum library to use. (ex: "v0.41.1")

    Returns:
        str: The reference documentation for the specified quantum method.
    """
    return request_reference(method_name, version)


if __name__ == "__main__":
    mcp.run(transport="stdio")
