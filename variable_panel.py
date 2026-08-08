from textual.widgets import DataTable

class VariablePanel(DataTable):
    """
    Visualizes historical variable states and deltas built from SQLite traces.
    Handles type parsing representations dynamically.
    """
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Variable Name", "Type Info", "Serialized Value Snapshot")

    def update_state(self, variables_dict: dict):
        """Clears rows and fills the grid with active delta states."""
        self.clear()
        for var_name, raw_repr in variables_dict.items():
            try:
                evaluated = eval(raw_repr)
                type_name = type(evaluated).__name__
            except Exception:
                type_name = "str"
            self.add_row(var_name, type_name, raw_repr)
