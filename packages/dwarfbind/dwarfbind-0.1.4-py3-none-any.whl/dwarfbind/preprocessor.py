"""
Header file preprocessing and macro extraction for dwarfbind.
"""

# Standard library imports
import importlib
import re
import subprocess

# Local imports
from .logging import logger
from .paths import resolve_header_or_directory_path


def process_headers(
    header_files: list[str],
    include_paths: list[str] = None,
    referenced_modules: list[str] = None,
) -> dict[str, str]:
    """
    Process C header files using cpp to extract macro definitions.

    Args:
        header_files: List of header files to process
        include_paths: Optional list of additional include paths
        referenced_modules: Optional list of pre-built modules to check for constants

    Returns:
        Dictionary mapping macro names to their values
    """
    # First try to import referenced modules and collect their constants
    existing_constants = {}
    if referenced_modules:
        import sys

        # Add current directory to path to find local modules
        if "" not in sys.path:
            sys.path.insert(0, "")

        for module_name in referenced_modules:
            try:
                # Import the module directly
                logger.debug(f"Importing module {module_name}")
                module = importlib.import_module(module_name)
                # Get the constants from the module's namespace
                for name in dir(module):
                    if not name.startswith("_"):
                        logger.debug(f"Found constant {name} in {module_name}")
                        existing_constants[name] = True
            except (ImportError, AttributeError) as e:
                logger.warning(
                    f"Could not import constants from {module_name}: {e}"
                )

    if not header_files:
        return {}

    # Build cpp command base with include paths
    cpp_cmd = ["cpp", "-dM"]
    if include_paths:
        for path in include_paths:
            cpp_cmd.extend(["-I", path])

    macros = {}

    def _strip_int_suffixes(value: str) -> str:
        # Remove common C integer literal suffixes (u/U, l/L in any combination)
        return re.sub(r"(?i)(?:[uUlL])+$", "", value)

    def _parse_cpp_output(text: str) -> None:
        for line in text.splitlines():
            if not line.strip().startswith("#define"):
                continue
            parts = line.split(None, 2)
            if len(parts) < 2:
                continue
            name = parts[1]
            value = parts[2] if len(parts) > 2 else None
            # Skip constants that are present in referenced modules
            if name in existing_constants:
                continue
            # Skip function-like macros and built-ins
            if "(" in name or name.startswith("__"):
                continue
            # Convert value to Python
            if value:
                try:
                    value = value.strip()
                    # Strip outer parentheses if present
                    while value.startswith("(") and value.endswith(")"):
                        value = value[1:-1].strip()
                    # Handle C-style casts
                    cast_patterns = [
                        r"\((void\s*\*|long|int|unsigned|float|double|char|short|size_t|unsigned\s+\w+)\s*\)",
                        r"\((const\s+)?(void\s*\*|char\s*\*)\s*\)",
                        r"\((unsigned\s+long(\s+long)?|long(\s+long)?(\s+int)?)\s*\)",
                    ]
                    for pattern in cast_patterns:
                        if re.match(pattern, value):
                            value = value.split(")", 1)[1].strip()
                            while value.startswith("(") and value.endswith(")"):
                                value = value[1:-1].strip()
                            break

                    # First, try generic integer parse with base auto-detection
                    try:
                        numeric = int(_strip_int_suffixes(value), 0)
                        value = str(numeric)
                    except Exception:
                        # Handle scientific notation floats
                        sci_match = re.match(r"^[+-]?\d+(?:\.\d+)?[eE][+-]?\d+(?:[fFlL])?$", value)
                        if sci_match:
                            # Strip float suffixes if present
                            suffix = value[-1]
                            if suffix in ("f", "F", "l", "L"):
                                value_num = value[:-1]
                            else:
                                value_num = value
                            try:
                                value = str(float(value_num))
                            except ValueError:
                                logger.debug(f"Invalid scientific float for {name}: {value}")
                                return
                        # Handle hex/octal numbers explicitly as fallback
                        elif value.startswith("0x") or value.startswith("0X"):
                            try:
                                value = _strip_int_suffixes(value)
                                value = str(int(value, 16))
                            except ValueError:
                                logger.debug(
                                    f"Invalid hex value for {name}: {value}"
                                )
                                return
                        elif value.startswith("0") and value not in ("0",):
                            try:
                                value = _strip_int_suffixes(value)
                                value = str(int(value, 8))
                            except ValueError:
                                logger.debug(
                                    f"Invalid octal value for {name}: {value}"
                                )
                                return
                        # Handle decimal numbers (ints and simple floats)
                        elif value.replace(".", "", 1).replace(
                            "l", "", 1
                        ).replace(
                            "L", "", 1
                        ).isdigit() or (
                            value.startswith("-") and value[1:].isdigit()
                        ):
                            try:
                                value = _strip_int_suffixes(value)
                                if "." in value:
                                    value = str(float(value))
                                else:
                                    value = str(int(value))
                            except ValueError:
                                logger.debug(
                                    f"Invalid decimal value for {name}: {value}"
                                )
                                return
                        # String literals
                        elif (
                            (value.strip().startswith('"') and value.strip().endswith('"'))
                            or (value.strip().startswith("'") and value.strip().endswith("'"))
                        ):
                            # Preserve raw contents (strip outer quotes) without decoding escapes
                            v = value.strip()
                            inner = v[1:-1]
                            value = repr(inner)
                        else:
                            # Any other value that still contains identifiers should be skipped
                            ident_tokens = re.findall(
                                r"[A-Za-z_][A-Za-z0-9_]*", value
                            )
                            if ident_tokens:
                                logger.debug(
                                    f"Skipping macro with unresolved identifiers {name} = {value}"
                                )
                                continue
                            logger.debug(
                                f"Skipping non-literal macro {name} = {value}"
                            )
                            continue
                    # Final validation - ensure it's a valid Python literal
                    try:
                        compile(value, "<string>", "eval")
                    except (SyntaxError, ValueError):
                        logger.debug(
                            f"Invalid Python literal for {name}: {value}"
                        )
                        continue
                except (ValueError, SyntaxError) as e:
                    logger.debug(f"Error processing {name}: {value} - {str(e)}")
                    continue
            else:
                value = "1"
            logger.debug(f"Adding constant {name} = {value}")
            macros[name] = value

    # Process each header file
    resolved_headers = []
    for header_or_directory in header_files:
        try:
            # Resolve header path using include paths
            resolved_paths = resolve_header_or_directory_path(header_or_directory, include_paths)
            resolved_headers.extend(resolved_paths)
            logger.debug(f"Resolved paths from {header_or_directory}: {resolved_paths}")
        except Exception as e:
            logger.warning(f"Error resolving {header_or_directory}: {e}")

    # Process each resolved header
    for resolved_header in resolved_headers:
        try:
            cmd = cpp_cmd + [resolved_header]
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning(
                    f"Failed to preprocess {resolved_header}: {result.stderr}"
                )
                continue
            _parse_cpp_output(result.stdout)

            # Generic fallback: capture simple numeric macros not added above
            try:
                for m in re.finditer(r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+([^\n]+)$", result.stdout, flags=re.MULTILINE):
                    name, raw = m.group(1), m.group(2).strip()
                    # Skip built-ins and function-like macros (pattern excludes '(' in name)
                    if name.startswith("__"):
                        continue
                    if name in macros or name in existing_constants:
                        continue
                    # strip outer parens
                    while raw.startswith("(") and raw.endswith(")"):
                        raw = raw[1:-1].strip()
                    # Accept only pure numeric literals (hex/oct/dec) with optional suffixes
                    try:
                        parsed = int(_strip_int_suffixes(raw), 0)
                    except Exception:
                        continue
                    macros[name] = str(parsed)
                    logger.debug(f"Adding constant {name} = {parsed} (numeric)")
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Error processing {resolved_header}: {e}")

    return macros


def parse_function_pointer_typedefs(header_files: list[str]) -> set[str]:
    """
    Scan header files and collect typedef names that define function pointers.
    This is a best-effort regex-based extractor to fill missing typedefs when
    DWARF info is not available.

    Returns:
        Set of typedef identifiers, e.g., {'ACQUIRE_CREDENTIALS_HANDLE_FN_A'}
    """
    fn_typedef_names: set[str] = set()
    if not header_files:
        return fn_typedef_names

    # Regex: typedef <ret> (<cc>* Name) (args...);
    pattern = re.compile(
        r"typedef\s+[^;\n]*\(\s*[^)]*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*\([^;]*\)\s*;"
    )

    # Resolve each header path (may expand to multiple files if directories)
    resolved_headers = []
    for path in header_files:
        try:
            resolved_paths = resolve_header_or_directory_path(path)
            resolved_headers.extend(resolved_paths)
        except Exception as e:
            logger.debug(f"Failed to resolve header path {path}: {e}")

    # Process each resolved header
    for resolved_path in resolved_headers:
        try:
            with open(resolved_path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
                for match in pattern.finditer(text):
                    name = match.group(1)
                    if name and name.isidentifier():
                        fn_typedef_names.add(name)
        except Exception as e:
            logger.debug(f"Failed to read header {resolved_path}: {e}")

    return fn_typedef_names
