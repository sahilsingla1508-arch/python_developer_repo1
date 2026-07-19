from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Label

from storage.storage import get_events


class VariablePanel(Widget):
    """
    Variable State Panel

    Displays variables recorded in SQLite.
    """

    def compose(self) -> ComposeResult:

        yield Label(
            "Variable State",
            id="variable_title"
        )

        table = DataTable(
            id="variable_table"
        )

        table.add_columns(
            "Variable",
            "Value",
            "Line"
        )

        events = get_events()

        if not events:

            table.add_row(
                "-",
                "No data",
                "-"
            )

        else:

            for event in events:

                table.add_row(
                    event["variable_name"],
                    event["serialized_value"],
                    str(event["line_number"])
                )

        yield table
