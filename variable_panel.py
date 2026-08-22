from rich.text import Text
from textual.widgets import DataTable


class VariablePanel(DataTable):
    """
    Visualizes historical variable states and deltas built from SQLite traces.
    Handles type parsing representations dynamically.

    Renders variable names in bold, type badges in muted style, and values
    with syntax-coloured Rich markup for professional appearance.
    """

    # Type-to-colour mapping for type badge colouring
    _TYPE_COLOURS = {
        "int":   "#79c0ff",
        "float": "#79c0ff",
        "bool":  "#ff7b72",
        "str":   "#a5d6ff",
        "list":  "#e3b341",
        "dict":  "#e3b341",
        "tuple": "#e3b341",
        "set":   "#e3b341",
        "NoneType": "#8b949e",
    }

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Variable", "Type", "Value")

    def update_state(self, variables_dict: dict):
        """Clears rows and fills the grid with active delta states."""
        self.clear()

        for var_name, raw_repr in variables_dict.items():
            # Determine type
            try:
                evaluated = eval(raw_repr)
                type_name = type(evaluated).__name__
            except Exception:
                evaluated = raw_repr
                type_name = "str"

            # Build Rich Text cells for professional styling
            name_cell = Text(var_name, style="bold #c9d1d9")

            type_colour = self._TYPE_COLOURS.get(type_name, "#8b949e")
            type_cell = Text(type_name, style=f"dim {type_colour}")

            # Value: show the actual value, not the JSON repr for strings
            if isinstance(evaluated, str):
                display_val = evaluated
            else:
                display_val = raw_repr

            # Truncate long values
            if len(display_val) > 42:
                display_val = display_val[:39] + "..."
            value_cell = Text(display_val, style="#a5d6ff")

            self.add_row(name_cell, type_cell, value_cell)