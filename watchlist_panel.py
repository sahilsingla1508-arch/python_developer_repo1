import ast

from textual.widgets import SelectionList
from textual.widgets.selection_list import Selection


class VariableDetector(ast.NodeVisitor):
    """Extract variable names assigned in the target Python script."""

    def __init__(self):
        self.variables = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)

        self.generic_visit(node)


class WatchlistPanel(SelectionList):
    """Interactive checklist for selecting variables to watch."""

    def __init__(self, target_script: str, **kwargs):
        super().__init__(**kwargs)
        self.target_script = target_script
        self.detected_vars = self._detect_variables()

    def _detect_variables(self) -> list[str]:
        """Parse the target script and return detected variable names."""
        try:
            with open(self.target_script, "r", encoding="utf-8") as file:
                source = file.read()

            tree = ast.parse(source)

            detector = VariableDetector()
            detector.visit(tree)

            return sorted(detector.variables)

        except (FileNotFoundError, SyntaxError, OSError):
            return []

    def on_mount(self) -> None:
        """Populate the watchlist when the panel is mounted."""
        for variable in self.detected_vars:
            self.add_option(
                Selection(
                    variable,
                    variable,
                    initial_state=True,
                )
            )

    def get_selected_variables(self) -> list[str]:
        """Return the variables currently selected by the user."""
        return list(self.selected)
