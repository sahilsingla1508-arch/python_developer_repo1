import ast


class VariableDetector(ast.NodeVisitor):
    """
    Visits an AST and collects all variable assignments.
    """

    def __init__(self):
        self.variables = []

    def visit_Assign(self, node):
        """
        Called automatically whenever an Assign node is found.
        """

        for target in node.targets:

            if isinstance(target, ast.Name):

                self.variables.append({
                    "name": target.id
                })

        self.generic_visit(node)


def detect_variables(tree):
    """
    Detect variables from an AST.

    Returns:
    [
        {"name": "total"},
        {"name": "count"}
    ]
    """

    detector = VariableDetector()

    detector.visit(tree)

    return detector.variables


if __name__ == "__main__":

    with open("sample_1.py", "r") as file:
        source = file.read()

    tree = ast.parse(source)

    variables = detect_variables(tree)

    print(variables)
