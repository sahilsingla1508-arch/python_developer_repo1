from textual.widgets import DataTable

class VariablePanel(DataTable):
    """Grid displaying active memory state reconstructed from SQLite delta logs."""
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Variable", "Type", "Delta Value")

    def update_state(self, variables_dict: dict, watch_filters: list[str] = None):
        """Clears and fills the state grid according to filter selections."""
        self.clear()
        for var_name, raw_repr in variables_dict.items():
            # Apply Watch Variables filtering if active
            if watch_filters and var_name not in watch_filters:
                continue
            try:
                evaluated = eval(raw_repr)
                type_name = type(evaluated).__name__
            except Exception:
                type_name = "str"
            self.add_row(var_name, type_name, raw_repr)
