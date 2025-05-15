from mcp.server.fastmcp import FastMCP

from tools.static_validation import static_validation

mcp = FastMCP(
    name="QuantumCodeValidator",
)


@mcp.tool(description="Validate quantum code by static analysis.")
def wrap_validate_static(code: str, version: str) -> dict:
    """Validate a static quantum code.

    This tool statically validates a quantum code by following steps:
    1. Check the syntax of the code by ast module.
    2. Check the compilation of the code by py_compile module.
    3. Check the usage of quantum library methods by comparing with the document of the specific version.

    Args:
        code (str): source code that includes quantum methods.
        version (str): The version of the quantum library to use. (ex: "v0.41.1")

    Returns:
        dict: A dictionary containing the validation results.
    """
    return static_validation(code, version)


if __name__ == "__main__":
    mcp.run(transport="stdio")
