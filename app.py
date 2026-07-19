from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer

from ui.code_viewer import CodeViewer
from ui.variable_panel import VariablePanel
from ui.timeline import TimelineWidget


class PyChronicleApp(App):
    """
    PyChronicle UI Skeleton

    Day 5
    Combines all widgets into one application layout.
    """

    TITLE = "PyChronicle"

    SUB_TITLE = "AST Powered Time Travel Debugger"

    CSS_PATH = "pychronicle.tcss"

    def compose(self) -> ComposeResult:

        yield Header(show_clock=True)

        with Vertical(id="main_layout"):

            with Horizontal(id="workspace"):

                yield CodeViewer()

                yield VariablePanel()

            yield TimelineWidget()

        yield Footer()


if __name__ == "__main__":
    PyChronicleApp().run()
