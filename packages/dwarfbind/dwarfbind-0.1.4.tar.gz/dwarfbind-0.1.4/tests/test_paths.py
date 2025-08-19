"""
Test path handling functionality.
"""

import os
import pytest

from dwarfbind.paths import (
    resolve_header_or_directory_path,
    collect_header_files_from_directory,
    generate_output_filename,
    strip_trailing_whitespace_from_file,
)


def test_collect_header_files_from_directory(tmp_path):
    """Test collecting all files from a directory."""
    # Create test directory structure
    subdir = tmp_path / "include"
    subdir.mkdir()

    # Create various files
    (tmp_path / "test.h").write_text("")
    (tmp_path / "other.hpp").write_text("")
    (subdir / "sub.h").write_text("")
    (tmp_path / "not_header.txt").write_text("")
    (subdir / "extra.hxx").write_text("")
    (subdir / "template.h++").write_text("")

    # Collect and verify
    headers = collect_header_files_from_directory(str(tmp_path))
    print("\nFound headers:", headers)  # Debug output
    assert len(headers) == 6
    assert all(os.path.isabs(h) for h in headers)
    assert any("test.h" in h for h in headers)
    assert any("other.hpp" in h for h in headers)
    assert any("sub.h" in h for h in headers)
    assert any("extra.hxx" in h for h in headers)
    assert any("template.h++" in h for h in headers)
    assert any("not_header.txt" in h for h in headers)


def test_resolve_header_or_directory_path_absolute(tmp_path):
    """Test resolving absolute paths to files and directories."""
    # Create test files
    header = tmp_path / "test.h"
    header.write_text("")
    subdir = tmp_path / "include"
    subdir.mkdir()
    (subdir / "sub.h").write_text("")

    # Test absolute file path
    resolved = resolve_header_or_directory_path(str(header))
    assert resolved == [str(header)]

    # Test absolute directory path
    resolved = resolve_header_or_directory_path(str(tmp_path))
    assert len(resolved) == 2
    assert all(h.endswith((".h", ".hpp", ".hxx", ".h++")) for h in resolved)


def test_resolve_header_or_directory_path_relative(tmp_path):
    """Test resolving relative paths against include paths."""
    # Create test structure in multiple include paths
    include1 = tmp_path / "include1"
    include2 = tmp_path / "include2"
    include1.mkdir()
    include2.mkdir()

    # Add headers to both include paths
    (include1 / "common.h").write_text("")
    (include2 / "common.h").write_text("")  # Same name, different location
    (include1 / "headers").mkdir()
    (include2 / "headers").mkdir()
    (include1 / "headers/test1.h").write_text("")
    (include2 / "headers/test2.h").write_text("")

    include_paths = [str(include1), str(include2)]

    # Test relative file path (first match wins)
    resolved = resolve_header_or_directory_path("common.h", include_paths)
    assert len(resolved) == 1
    assert resolved[0] == str(include1 / "common.h")

    # Test relative directory path (combines matches from all paths)
    resolved = resolve_header_or_directory_path("headers", include_paths)
    assert len(resolved) == 2
    assert any("test1.h" in h for h in resolved)
    assert any("test2.h" in h for h in resolved)


def test_resolve_header_or_directory_path_missing():
    """Test handling of missing files and directories."""
    # Non-existent path with no include paths
    resolved = resolve_header_or_directory_path("missing.h")
    assert resolved == ["missing.h"]  # Returns original for cpp to handle

    # Non-existent directory
    resolved = resolve_header_or_directory_path("missing/")
    assert resolved == []  # Empty list for directories that don't exist


def test_generate_output_filename():
    """Test output filename generation."""
    assert generate_output_filename("libtest.so.1", "") == "libtest_so_1.py"
    assert generate_output_filename(None, "/path/to/lib.so") == "lib_so.py"
    assert generate_output_filename("", "lib-test.so") == "lib_test_so.py"


def test_strip_trailing_whitespace(tmp_path):
    """Test whitespace stripping from files."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("line1  \nline2\t \nline3\n")

    strip_trailing_whitespace_from_file(str(test_file))
    content = test_file.read_text()

    assert content == "line1\nline2\nline3\n"
    assert not any(line.rstrip() != line.rstrip(" \t") for line in content.splitlines())
