"""Tests for usage example generation."""

import io
import sys
from unittest.mock import patch

from dwarfbind.generator import print_usage_example


def test_usage_example_includes_constant_when_available(capsys):
    """Usage example should include a real constant when macros are provided."""
    example = {
        "function": "test_func",
        "struct": "TestStruct",
        "field": "count",
        "argtypes": "[POINTER(TestStruct)]",
        "call_args": "byref(structure)",
    }

    with patch("dwarfbind.generator.find_usage_example", return_value=example):
        print_usage_example(
            debug_files=None,
            all_structures={},
            all_typedefs={},
            output_filename="test_lib.py",
            use_color=False,  # Disable color for predictable output
            macros={"MAX_COUNT": "100", "__internal": "0", "123invalid": "456"},
        )

    captured = capsys.readouterr()
    assert "from test_lib.constants import MAX_COUNT" in captured.out
    assert "structure.count = MAX_COUNT" in captured.out
    assert "# structure.count = 0" not in captured.out


def test_usage_example_falls_back_when_no_constants():
    """Usage example should use placeholder when no macros are available."""
    example = {
        "function": "test_func",
        "struct": "TestStruct",
        "field": "count",
        "argtypes": "[POINTER(TestStruct)]",
        "call_args": "byref(structure)",
    }

    # Capture stdout to string buffer
    stdout = io.StringIO()
    with patch("sys.stdout", stdout):
        with patch("dwarfbind.generator.find_usage_example", return_value=example):
            print_usage_example(
                debug_files=None,
                all_structures={},
                all_typedefs={},
                output_filename="test_lib.py",
                use_color=False,  # Disable color for predictable output
                macros=None,
            )

    output = stdout.getvalue()
    assert "from test_lib.constants import" not in output
    assert "# structure.count = 0  # set fields as needed" in output


def test_usage_example_skips_invalid_constant_names():
    """Usage example should skip invalid identifiers when selecting constants."""
    example = {
        "function": "test_func",
        "struct": "TestStruct",
        "field": "count",
        "argtypes": "[POINTER(TestStruct)]",
        "call_args": "byref(structure)",
    }

    # Only provide invalid names
    with patch("dwarfbind.generator.find_usage_example", return_value=example):
        with patch("sys.stdout", io.StringIO()) as fake_stdout:
            print_usage_example(
                debug_files=None,
                all_structures={},
                all_typedefs={},
                output_filename="test_lib.py",
                use_color=False,  # Disable color for predictable output
                macros={"123invalid": "456", "__internal": "0", "!bad": "1"},
            )

    output = fake_stdout.getvalue()
    assert "from test_lib.constants import" not in output
    assert "# structure.count = 0  # set fields as needed" in output


def test_usage_example_prefers_simple_constant_names():
    """Usage example should prefer simple, readable constant names."""
    example = {
        "function": "test_func",
        "struct": "TestStruct",
        "field": "count",
        "argtypes": "[POINTER(TestStruct)]",
        "call_args": "byref(structure)",
    }

    # Mix of complex and simple names - should pick SIMPLE
    with patch("dwarfbind.generator.find_usage_example", return_value=example):
        with patch("sys.stdout", io.StringIO()) as fake_stdout:
            print_usage_example(
                debug_files=None,
                all_structures={},
                all_typedefs={},
                output_filename="test_lib.py",
                use_color=False,  # Disable color for predictable output
                macros={
                    "COMPLEX_VERY_LONG_NAME": "1",
                    "SIMPLE": "2",
                    "__INTERNAL_THING": "3",
                },
            )

    output = fake_stdout.getvalue()
    assert "from test_lib.constants import SIMPLE" in output
    assert "structure.count = SIMPLE" in output 