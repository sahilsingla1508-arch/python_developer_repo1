import ast


def parse_file(filepath: str) -> ast.Module:
    with open(filepath, "r") as f:
        source_code = f.read()
    tree = ast.parse(source_code, filename=filepath)
    return tree


def print_node_types(tree: ast.Module) -> None:
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        print(f"line {line}: {type(node).__name__}")


def find_assignments(tree: ast.Module) -> list[tuple[int, str]]:
    assignments: list[tuple[int, str]] = []

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


def _collect_names(target, lineno, out_list) -> None:
    if isinstance(target, ast.Name):
        out_list.append((lineno, target.id))
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            _collect_names(elt, lineno, out_list)


if __name__ == "__main__":
    # "sample_1.py" seedha likha hai kyunki ye file bhi ab
    # usi (root) folder mein hai — koi subfolder nahi.
    tree = parse_file("sample_1.py")

    print("=== Full node dump ===")
    print(ast.dump(tree, indent=2))

    print("\n=== Every node type + line ===")
    print_node_types(tree)

    print("\n=== Just the assignments ===")
    for line, name in find_assignments(tree):
        print(f"line {line}: {name}")