import ast
import json


def parse_file(filepath: str) -> ast.Module:
    """
    Read a Python file and return its AST.
    """
    with open(filepath, "r") as f:
        source_code = f.read()

    tree = ast.parse(source_code, filename=filepath)
    return tree


def print_node_types(tree: ast.Module) -> None:
    """
    Print every node type with its line number.
    """
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        print(f"line {line}: {type(node).__name__}")


def find_assignments(tree: ast.Module) -> list[tuple[int, str]]:
    """
    Find all variable assignments.
    Returns:
        [
            (2, "total"),
            (3, "count"),
            ...
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
    Collect variable names from assignment targets.
    """

    if isinstance(target, ast.Name):
        out_list.append((lineno, target.id))

    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            _collect_names(elt, lineno, out_list)


# ----------------------------
# NEW FUNCTION
# ----------------------------

def export_assignments(tree: ast.Module) -> list[dict]:
    """
    Convert detected assignments into JSON-serializable dictionaries.

    Example Output:
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
    Main API for downstream modules.

    Returns JSON-serializable data.
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