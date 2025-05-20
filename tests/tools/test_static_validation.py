from typing import cast
from unittest import mock

import pytest

from src.tools.static_validation import (
    TMP_CODE_PATH,
    _extract_method_name,
    _extract_pennylane_methods,
    _is_optional_type,
    _validate_args,
    validate_by_ast,
    validate_by_py_compile,
    validate_pennylane_code_statically,
    validate_pennylane_methods,
)


@pytest.mark.parametrize(
    "code,should_pass",
    [
        ("a = 1", True),
        ("def f():\n  return 1", True),
        ("def f(\n", False),
    ],
)
def test_validate_by_ast(code, should_pass):
    result = validate_by_ast(code)
    assert isinstance(result["errors"], list)
    if should_pass:
        assert result["valid"] is True
        assert result["errors"] == []
    else:
        assert result["valid"] is False
        assert result["errors"]


@pytest.mark.parametrize(
    "code,should_pass",
    [
        ("a = 1", True),
        ("def f():\n  return 1", True),
        ("def f(\n", False),
    ],
)
def test_validate_by_py_compile(code, should_pass, tmp_path):
    result = validate_by_py_compile(code, tmp_path / TMP_CODE_PATH)
    assert isinstance(result["errors"], list)
    if should_pass:
        assert result["valid"] is True
        assert result["errors"] == []
    else:
        assert result["valid"] is False
        assert result["errors"]

    assert not (tmp_path / TMP_CODE_PATH).exists()


@pytest.mark.parametrize(
    "code,expected",
    [
        ("qml.RX(0.5, wires=0)", ["qml.RX(0.5, wires=0)"]),
        ("qml.RX(0.5, wires=0) + qml.RY(1.0, wires=1)", ["qml.RX(0.5, wires=0)", "qml.RY(1.0, wires=1)"]),
        ("import pennylane as qml\nqml.device('default.qubit', wires=2)", ["qml.device('default.qubit', wires=2)"]),
        ("a = 1", []),
    ],
)
def test_extract_pennylane_methods(code, expected):
    result = _extract_pennylane_methods(code)
    assert set(result) == set(expected)


@pytest.mark.parametrize(
    "method_code_str,expected",
    [
        ("qml.RX(0.5, wires=0)", "qml.RX"),
        ("qml.RY(1.0, wires=1)", "qml.RY"),
        ("qml.device('default.qubit', wires=2)", "qml.device"),
        ("a = 1", ""),
    ],
)
def test_extract_method_name(method_code_str, expected):
    assert _extract_method_name(method_code_str) == expected


@pytest.mark.parametrize(
    "type_str,expected",
    [
        ("Optional[int]", True),
        ("Union[int, None]", True),
        ("int | None", True),
        ("int or None", True),
        ("int", False),
        ("str", False),
    ],
)
def test_is_optional_type(type_str, expected):
    assert _is_optional_type(type_str) == expected


@pytest.mark.parametrize(
    "method,expected_args,expected_errors",
    [
        (
            "qml.RX(0.5, wires=0)",
            [
                {"name": "phi", "required": True, "type": "float", "description": "The rotation angle"},
                {"name": "wires", "required": True, "type": "int", "description": "The wire the operation acts on"},
            ],
            [],
        ),
        (
            "qml.RX(phi=0.5, wires=0)",
            [
                {"name": "phi", "required": True, "type": "float", "description": "The rotation angle"},
                {"name": "wires", "required": True, "type": "int", "description": "The wire the operation acts on"},
            ],
            [],
        ),
        (
            "qml.RX(wires=0)",
            [
                {"name": "phi", "required": True, "type": "float", "description": "The rotation angle"},
                {"name": "wires", "required": True, "type": "int", "description": "The wire the operation acts on"},
            ],
            [
                "Missing required argument 'phi'.\nphi (float): The rotation angle",
            ],
        ),
        (
            "qml.RX(theta=0.5, wires=0)",
            [
                {"name": "phi", "required": True, "type": "float", "description": "The rotation angle"},
                {"name": "wires", "required": True, "type": "int", "description": "The wire the operation acts on"},
            ],
            [
                "Missing required argument 'phi'.\nphi (float): The rotation angle",
                "Unexpected argument 'theta'",
            ],
        ),
        (
            "qml.RX(0.5, wires=0, foo=1)",
            [
                {"name": "phi", "required": True, "type": "float", "description": "The rotation angle"},
                {"name": "wires", "required": True, "type": "int", "description": "The wire the operation acts on"},
            ],
            ["Unexpected argument 'foo'"],
        ),
    ],
)
def test_validate_args(method, expected_args, expected_errors):
    errors = _validate_args(method, expected_args)
    assert set(errors) == set(expected_errors)


# validate_pennylane_methods
@mock.patch("src.tools.static_validation.get_reference")
def test_validate_pennylane_methods(mock_get_ref):
    mock_get_ref.return_value = {
        "qml.RX": {
            "args": [
                {"name": "phi", "required": True},
                {"name": "wires", "required": True},
                {"name": "id", "required": False},
            ]
        },
        "qml.RY": {
            "args": [
                {"name": "phi", "required": True},
                {"name": "wires", "required": True},
                {"name": "id", "required": False},
            ]
        },
    }
    code = "import pennylane as qml\nqml.RX(0.5, wires=0)\nqml.RY(phi=1.0, wires=1)"
    result = validate_pennylane_methods(code, version="v0.41.0")
    assert result["valid"] is True
    assert result["errors"] == []

    code2 = "qml.RX(wires=0)\nqml.RY(phi=1.0, wires=1)"
    result2 = validate_pennylane_methods(code2, version="v0.41.0")
    assert result2["valid"] is False
    assert any("Missing required argument 'phi'" in e for e in cast(list[str], result2["errors"]))


# validate_pennylane_code_statically
@mock.patch("src.tools.static_validation.validate_by_ast")
@mock.patch("src.tools.static_validation.validate_by_py_compile")
@mock.patch("src.tools.static_validation.validate_pennylane_methods")
def test_validate_pennylane_code_statically(mock_pl, mock_py, mock_ast):
    mock_ast.return_value = {"valid": True, "errors": []}
    mock_py.return_value = {"valid": True, "errors": []}
    mock_pl.return_value = {"valid": True, "errors": []}
    result = validate_pennylane_code_statically("qml.RX(0.5, wires=0)")
    assert result["valid"] is True
    assert result["errors"] == []

    mock_ast.return_value = {"valid": False, "errors": ["SyntaxError"]}
    mock_py.return_value = {"valid": True, "errors": []}
    mock_pl.return_value = {"valid": True, "errors": []}
    result2 = validate_pennylane_code_statically("def f(\n")
    assert result2["valid"] is False
    assert any("SyntaxError" in e for e in cast(list[str], result2["errors"]))
