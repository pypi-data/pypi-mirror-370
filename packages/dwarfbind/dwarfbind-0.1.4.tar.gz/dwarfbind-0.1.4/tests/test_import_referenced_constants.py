"""Regression test: importing constants from a generated module that references
another generated module should work (no variable shadowing in generator).

This test builds two tiny shared libraries locally and a header defining
one macro. It avoids any dependency on system packages.
"""
import os
import shutil
import subprocess
import sys
import textwrap

import pytest


def run_capture(cmd: list[str]) -> subprocess.CompletedProcess:
	return subprocess.run(cmd, capture_output=True, text=True)


@pytest.mark.integration
@pytest.mark.skipif(shutil.which("cc") is None, reason="C compiler not available")
def test_import_constants_with_local_referenced_module(tmp_path):
	# Build a tiny dependency shared library with an SONAME
	dep_c = tmp_path / "dep.c"
	dep_so = tmp_path / "libdep.so.1.0.0"
	dep_c.write_text("int dep(void){return 42;}\n", encoding="utf-8")
	res = run_capture([
		"cc",
		"-g",
		"-fPIC",
		"-shared",
		"-Wl,-soname,libdep.so.1",
		"-o",
		str(dep_so),
		str(dep_c),
	])
	assert res.returncode == 0, res.stderr

	# Build a tiny main shared library with an SONAME
	main_c = tmp_path / "main.c"
	main_so = tmp_path / "libmain.so.1.0.0"
	main_c.write_text("int mainfoo(void){return 7; }\n", encoding="utf-8")
	res = run_capture([
		"cc",
		"-g",
		"-fPIC",
		"-shared",
		"-Wl,-soname,libmain.so.1",
		"-o",
		str(main_so),
		str(main_c),
	])
	assert res.returncode == 0, res.stderr

	# Local header providing a simple macro constant
	header = tmp_path / "test.h"
	header.write_text("#define FAR 1\n", encoding="utf-8")

	cwd = os.getcwd()
	try:
		os.chdir(tmp_path)
		# Generate dependency bindings first: positional library path first
		r1 = run_capture(["uv", "run", "dwarfbind", str(dep_so), "--headers", str(header)])
		assert r1.returncode == 0, r1.stderr

		# Then generate main bindings, referencing the dependency module by name
		# Positional library path first to avoid headers capturing it
		r2 = run_capture([
			"uv",
			"run",
			"dwarfbind",
			str(main_so),
			"--modules",
			"libdep_so_1",
			"--headers",
			str(header),
		])
		assert r2.returncode == 0, r2.stderr

		# Ensure we can import the constant from the main module's constants submodule
		code = textwrap.dedent(
			"""
			from libmain_so_1.constants import FAR
			print(FAR)
			"""
		)
		proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
		assert proc.returncode == 0, proc.stderr
		assert proc.stdout.strip() == "1"
	finally:
		os.chdir(cwd)
