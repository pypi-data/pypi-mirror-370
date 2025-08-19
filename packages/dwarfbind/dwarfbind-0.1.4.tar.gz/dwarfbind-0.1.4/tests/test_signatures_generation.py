"""
Tests for DWARF-derived function signatures emission and symbols accessor behavior.
"""

from unittest.mock import MagicMock

from dwarfbind.debug_info import (
	StructMember,
	StructureDefinition,
	TypedefInfo,
	QualityScore,
)
from dwarfbind.generator import generate_python_module


def test_generate_module_includes_signature_dict_entries(temp_file):
	"""Verify EXPORT_SYMBOLS is a dict with per-function signature specs."""
	# Minimal struct to reference in argtypes
	structures = {("TestStruct", 8): StructureDefinition("TestStruct", 8)}
	structures[("TestStruct", 8)].members = [
		StructMember(0, "field1", "c_int", "test field"),
	]

	typedefs = {
		"TestTypedef": TypedefInfo(
			"c_void_p",
			QualityScore(base_score=3, size_score=1),
			"test typedef",
		)
	}

	exported_functions = ["test_function", "other_function"]
	function_signatures = {
		"test_function": {
			"restype": "c_int",
			"argtypes": ["POINTER(types.TestStruct)"],
		}
	}

	generate_python_module(
		temp_file,
		"libtest.so",
		str(temp_file),
		"test-build-id",
		structures,
		typedefs,
		exported_functions,
		function_signatures,
		{"TEST_MACRO": "42"},
	)

	with open(temp_file, "r") as f:
		content = f.read()

	# Dict header present
	assert "EXPORT_SYMBOLS = {" in content
	# Entry with provided signature
	assert (
		"'test_function': {'restype': 'c_int', 'argtypes': ['POINTER(types.TestStruct)']}"
		in content
	)
	# Entry for function without signature present with defaults
	assert "'other_function': {'restype': None, 'argtypes': []}" in content


def test_generated_symbols_accessor_sets_prototypes_code_present(temp_file):
	"""Verify the generated module includes logic to set restype/argtypes and dir uses keys."""
	structures = {}
	typedefs = {}
	exported_functions = ["fn"]
	function_signatures = {"fn": {"restype": "c_int", "argtypes": ["c_int"]}}

	generate_python_module(
		temp_file,
		"libt.so",
		str(temp_file),
		"build",
		structures,
		typedefs,
		exported_functions,
		function_signatures,
	)

	with open(temp_file, "r") as f:
		content = f.read()

	# __getattr__ contains eval to set prototypes
	assert "eval(restype_expr" in content
	assert "eval(e, globals(), locals())" in content
	# __dir__ uses EXPORT_SYMBOLS.keys()
	assert "EXPORT_SYMBOLS.keys()" in content 