from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Label


class VariablePanel(Widget):
    """
    Displays program variables.

    Day 3:
    Uses static dummy data.
    """

    VARIABLES = {
        "x": 5,
        "y": 8,
        "result": 13,
        "status": "Running",
        "flag": True,
    }

    def compose(self) -> ComposeResult:
        yield Label("Variable State", id="variable_title")

        table = DataTable(id="variable_table")
        table.add_columns("Variable", "Value")

        for name, value in self.VARIABLES.items():
            table.add_row(name, str(value))

        yield table
