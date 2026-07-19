import ast


class VariableDetector(ast.NodeVisitor):
    """
    Detects variable assignments from a Python AST.

    Supports optional scope filtering:
    - Function name
    - Line range
    """

    def __init__(self, scope=None):
        self.variables = []
        self.scope = scope

        # Stack to keep track of current function
        self.function_stack = []

    def visit_FunctionDef(self, node):
        """
        Track the current function while visiting.
        """
        self.function_stack.append(node.name)

        self.generic_visit(node)

        self.function_stack.pop()

    def visit_Assign(self, node):

        if not self._inside_scope(node):
            return

        for target in node.targets:

            if isinstance(target, ast.Name):

                self.variables.append(
                    {
                        "name": target.id,
                        "line": node.lineno,
                        "function": (
                            self.function_stack[-1]
                            if self.function_stack
                            else "global"
                        ),
                    }
                )

        self.generic_visit(node)

    def _inside_scope(self, node):
        """
        Returns True if this assignment matches the requested scope.
        """

        if self.scope is None:
            return True

        # -----------------------------
        # Function filtering
        # -----------------------------
        if "function" in self.scope:

            current = (
                self.function_stack[-1]
                if self.function_stack
                else "global"
            )

            return current == self.scope["function"]

        # -----------------------------
        # Line range filtering
        # -----------------------------
        if "lines" in self.scope:

            start, end = self.scope["lines"]

            return start <= node.lineno <= end

        return True


def detect_variables(tree, scope=None):
    """
    Detect variables from an AST.

    Parameters
    ----------
    tree : ast.Module

    scope : dict | None

    Examples
    --------

    detect_variables(tree)

    detect_variables(
        tree,
        scope={"function": "calculate"}
    )

    detect_variables(
        tree,
        scope={"lines": (5, 15)}
    )
    """

    detector = VariableDetector(scope)

    detector.visit(tree)

    return detector.variables


if __name__ == "__main__":

    with open("sample_1.py", "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    print("\nAll Variables")
    print(detect_variables(tree))

    print("\nVariables in function 'calculate'")
    print(
        detect_variables(
            tree,
            scope={"function": "calculate"}
        )
    )

    print("\nVariables between lines 1 and 10")
    print(
        detect_variables(
            tree,
            scope={"lines": (1, 10)}
        )
    )
