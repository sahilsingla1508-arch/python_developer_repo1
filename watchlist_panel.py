import ast

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widgets import SelectionList
from textual.widgets.selection_list import Selection
from textual.widgets._option_list import OptionDoesNotExist, OptionList


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
    """
    Interactive checklist for selecting variables to watch.

    Each detected variable is pre-selected. Unchecking a variable
    removes it from the variable panel filter.

    Displays clean circular status indicators (● / ○) instead of default X checkboxes.
    """

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

    def render_line(self, y: int) -> Strip:
        """Render a line with clean circular status indicators (● / ○) instead of X buttons."""
        _, scroll_y = self.scroll_offset
        selection_index = scroll_y + y
        try:
            selection = self.get_option_at_index(selection_index)
        except OptionDoesNotExist:
            return super().render_line(y)

        # Get base prompt line from OptionList
        line = super(SelectionList, self).render_line(y)

        is_selected = selection.value in self._selected
        component_style = "selection-list--button"
        if is_selected:
            component_style += "-selected"
        if self.highlighted == selection_index:
            component_style += "-highlighted"

        underlying_style = next(iter(line)).style or self.rich_style
        button_style = self.get_component_rich_style(component_style)

        side_style = Style.from_color(button_style.bgcolor, underlying_style.bgcolor)
        side_style += Style(meta={"option": selection_index})
        button_style += Style(meta={"option": selection_index})

        dot_glyph = "●" if is_selected else "○"

        return Strip(
            [
                Segment(" ", style=side_style),
                Segment(dot_glyph, style=button_style),
                Segment("  ", style=underlying_style),
                *line,
            ]
        )

    def get_selected_variables(self) -> list[str]:
        """Return the variables currently selected by the user."""
        return list(self.selected)