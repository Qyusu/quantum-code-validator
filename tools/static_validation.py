import ast
import json
import os
import py_compile
import re
from typing import Optional, cast

from scripts.common import get_latest_version
from scripts.constants import REF_DOCS_DIR

TMP_CODE_PATH = "tmp_code.py"


def validate_by_ast(code: str) -> dict[str, bool | list[str]]:
    try:
        ast.parse(code)
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {"valid": False, "errors": [f"SyntaxError: {e}"]}


def validate_by_py_compile(code: str) -> dict[str, bool | list[str]]:
    try:
        # write to tmp python file for compile
        with open(TMP_CODE_PATH, "w") as file:
            file.write(code)
        py_compile.compile(TMP_CODE_PATH, doraise=True)
        # remove tmp python file
        os.remove(TMP_CODE_PATH)
        return {"valid": True, "errors": []}
    except py_compile.PyCompileError as e:
        return {"valid": False, "errors": [f"py_compile: Syntax error: {e}"]}


def _extract_pennylane_methods(code: str) -> list[str]:
    functions = []
    start_idx = code.find("qml.")  # Start by looking for "qml." pattern
    while start_idx != -1:
        # Track the position and initialize a stack to manage parentheses
        end_idx = start_idx
        stack = []

        # Process each character after the "qml." pattern to balance parentheses
        while end_idx < len(code):
            char = code[end_idx]
            if char == "(":
                stack.append(char)  # Push opening parenthesis
            elif char == ")":
                if stack:
                    stack.pop()  # Pop closing parenthesis
                else:
                    break
                if not stack:  # If stack is empty, parentheses are balanced
                    functions.append(code[start_idx : end_idx + 1])
                    break
            end_idx += 1

        # Continue searching for the next "qml." pattern
        start_idx = code.find("qml.", end_idx)

    return list(set(functions))


def get_reference(version: str) -> dict[str, dict[str, list[dict[str, str]]]]:
    reference_path = os.path.join(f"{REF_DOCS_DIR}/pennylane/format", f"{version}.json")
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"Reference file not found: {reference_path}")
    with open(reference_path) as f:
        return json.load(f)


def _extract_method_name(code_str: str) -> str:
    tree = ast.parse(code_str)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                return f"{node.func.value.id}.{node.func.attr}"  # type: ignore

    return ""


def _is_optional_type(type_str: str) -> bool:
    type_str = type_str.replace(" ", "")

    # pattern1: Optional[<type>]
    if re.match(r"^Optional\[[^\[\]]+\]$", type_str):
        return True

    # pattern2: Union[..., None] or Union[None, ...]
    if re.match(r"^Union\[.*None.*\]$", type_str):
        return True

    # pattern3: <type> | None
    if "|" in type_str:
        parts = type_str.split("|")
        if "None" in parts:
            return True

    # patter4: <type> or None
    if "or" in type_str:
        parts = type_str.split("or")
        if "None" in parts:
            return True

    return False


def _validate_args(method: str, expected_args: list[dict[str, str]]) -> list[str]:
    errors = []
    expected_args_names = [arg["name"] for arg in expected_args]
    tree = ast.parse(method)

    for node in ast.walk(tree):
        # check only qml.XXX method call
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "qml"
        ):
            provided_args = {}

            # handle positional arguments
            for i, arg in enumerate(node.args):
                if i < len(expected_args):
                    provided_args[expected_args[i]["name"]] = arg

            # handle keyword arguments
            for keyword in node.keywords:
                provided_args[keyword.arg] = keyword.value

            # check unexpected arguments
            for arg in provided_args.keys():
                if arg not in expected_args_names:
                    errors.append(f"Unexpected argument '{arg}'")

            # check arguments existence and types
            for expected_arg in expected_args:
                arg_name = expected_arg["name"]
                arg_type = expected_arg["type"]
                if arg_name not in provided_args and not _is_optional_type(arg_type):
                    errors.append(f"Missing required argument '{arg_name}'")

            # only one method call is allowed
            break

    return errors


def validate_pennylane_methods(code: str, version: Optional[str] = None) -> dict[str, bool | list[str]]:
    if version is None:
        version = get_latest_version()

    version = f"v{version}" if not version.startswith("v") else version
    reference = get_reference(version)

    errors = []
    pennylane_methods = _extract_pennylane_methods(code)
    for method in pennylane_methods:
        method_errors = []
        method_name = _extract_method_name(method)
        signature = reference.get(method_name)
        if signature is None:
            method_errors.append(f"Method '{method_name}' not found in PennyLane version '{version}'")
        else:
            expected_args = signature["args"]
            args_erros = _validate_args(method, expected_args)
            method_errors.extend(args_erros)

        if method_errors:
            method_errors_str = ", ".join(method_errors)
            errors.append(f"Method '{method_name}': {method_errors_str}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_pennylane_code_statically(code: str, version: Optional[str] = None) -> dict[str, bool | list[str]]:
    ast_errors = validate_by_ast(code)
    py_compile_errors = validate_by_py_compile(code)
    pennylane_errors = validate_pennylane_methods(code, version)

    return {
        "valid": ast_errors["valid"] and py_compile_errors["valid"] and pennylane_errors["valid"],
        "errors": cast(list[str], ast_errors["errors"])
        + cast(list[str], py_compile_errors["errors"])
        + cast(list[str], pennylane_errors["errors"]),
    }
