import ast
from textual.widgets import SelectionList
from textual.widgets.selection_list import Selection

class VariableDetector(ast.NodeVisitor):
    """Traverses Python AST to extract all declared variable targets."""
    def __init__(self):
        self.variables = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
        self.generic_visit(node)

class WatchlistPanel(SelectionList):
    """Interactive Checkbox selection panel for filtering tracked variables."""
    def __init__(self, target_script: str, **kwargs):
        super().__init__(**kwargs)
        self.target_script = target_script
        self.detected_vars = self._detect_variables()

    def _detect_variables(self) -> list[str]:
        try:
            with open(self.target_script, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            detector = VariableDetector()
            detector.visit(tree)
            return sorted(list(detector.variables))
        except Exception:
            return []

    def on_mount(self) -> None:
        for var in self.detected_vars:
            self.add_option(Selection(var, var, initial_state=True))
