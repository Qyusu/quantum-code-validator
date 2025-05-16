import json
import os
from typing import Optional

from scripts.common import get_latest_version
from scripts.constants import REF_DOCS_DIR


def request_reference(method_name: str, version: Optional[str] = None) -> str:
    """Request reference documentation for a specific method in a specific version of the quantum library.

    Args:
        method_name (str): The name of the method to request reference documentation.
        version (Optional[str]): The version of the quantum library to use.

    Returns:
        str: The reference documentation for the specified quantum method.
    """
    if version is None:
        version = get_latest_version()

    version = f"v{version}" if not version.startswith("v") else version

    reference_path = os.path.join(f"{REF_DOCS_DIR}/pennylane/raw", f"{version}.json")
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"Reference file not found: {reference_path}")
    with open(reference_path) as f:
        reference = json.load(f)

    if method_name not in reference:
        raise ValueError(f"Method '{method_name}' not found in reference: {reference_path}")
    else:
        reference_doc = f"""
        # {method_name}

        # Signature
        {reference[method_name]["signature"]}

        # Docstring
        {reference[method_name]["docstring"]}

        # Source Code
        {reference[method_name]["source"]}
        """

    return reference_doc
