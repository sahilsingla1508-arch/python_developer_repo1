"""
AST Parser Module

This module parses Python source code using Python's built-in `ast` module.
It detects variable assignments and exports them in a JSON-serializable format
for downstream modules.

Features:
- Parse Python source files
- Detect variable assignments
- Support Assign, AugAssign, and AnnAssign nodes
- Export assignment information as JSON-ready data
"""

import ast
import json


def parse_file(filepath: str) -> ast.Module:
    """
    Read a Python source file and return its Abstract Syntax Tree (AST).

    Args:
        filepath: Path to the Python source file.

    Returns:
        Parsed AST module.
    """
    with open(filepath, "r") as f:
        source_code = f.read()

    tree = ast.parse(source_code, filename=filepath)
    return tree


def print_node_types(tree: ast.Module) -> None:
    """
    Print every AST node type along with its corresponding line number.

    Useful for debugging and understanding the structure of parsed code.

    Args:
        tree: Parsed AST module.
    """
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        print(f"line {line}: {type(node).__name__}")


def find_assignments(tree: ast.Module) -> list[tuple[int, str]]:
    """
    Traverse the AST and collect all variable assignments.

    Supported node types:
    - Assign
    - AugAssign
    - AnnAssign

    Args:
        tree: Parsed AST module.

    Returns:
        A list of tuples in the format:

            (line_number, variable_name)

    Example:

        [
            (2, "total"),
            (3, "count")
        ]
    """
    assignments = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):
            for target in node.targets:
                _collect_names(target, node.lineno, assignments)

        elif isinstance(node, ast.AugAssign):
            _collect_names(node.target, node.lineno, assignments)

        elif isinstance(node, ast.AnnAssign):
            _collect_names(node.target, node.lineno, assignments)

    assignments.sort(key=lambda pair: pair[0])

    return assignments


def _collect_names(target, lineno, out_list):
    """
    Recursively extract variable names from assignment targets.

    Supports:
    - Single variable assignments
    - Tuple unpacking
    - List unpacking

    Args:
        target: AST assignment target.
        lineno: Line number of assignment.
        out_list: List used to collect detected variables.
    """

    if isinstance(target, ast.Name):
        out_list.append((lineno, target.id))

    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            _collect_names(elt, lineno, out_list)


def export_assignments(tree: ast.Module) -> list[dict]:
    """
    Convert detected assignments into JSON-serializable dictionaries.

    Args:
        tree: Parsed AST module.

    Returns:
        List of dictionaries.

    Example:

        [
            {
                "line_number": 2,
                "variable_name": "total"
            }
        ]
    """

    assignments = find_assignments(tree)

    result = []

    for line, variable in assignments:

        result.append(
            {
                "line_number": line,
                "variable_name": variable,
            }
        )

    return result


def analyze(filepath: str) -> list[dict]:
    """
    High-level API for the AST parser.

    Reads a Python source file, detects assignments,
    and returns JSON-ready data for downstream modules.

    Args:
        filepath: Path to the Python source file.

    Returns:
        List of assignment dictionaries.
    """

    tree = parse_file(filepath)

    return export_assignments(tree)


if __name__ == "__main__":

    tree = parse_file("sample_1.py")

    print("========== AST ==========")
    print(ast.dump(tree, indent=2))

    print("\n========== NODE TYPES ==========")
    print_node_types(tree)

    print("\n========== ASSIGNMENTS ==========")
    assignments = find_assignments(tree)

    for line, variable in assignments:
        print(f"Line {line} -> {variable}")

    print("\n========== JSON EXPORT ==========")

    json_output = analyze("sample_1.py")

    print(json.dumps(json_output, indent=4))