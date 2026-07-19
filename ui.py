from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical


class PyChronicleApp(App):
    """
    PyChronicle
    AST Powered Time Travel Debugger

    Week 2
    UI Skeleton
    """

    TITLE = "PyChronicle"
    SUB_TITLE = "AST Powered Time Travel Debugger"

    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:

        yield Header(show_clock=True)

        yield Vertical(

            Static(
                """
██████╗ ██╗   ██╗ ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗██╗ ██████╗██╗     ███████╗
██╔══██╗╚██╗ ██╔╝██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██║     ██╔════╝
██████╔╝ ╚████╔╝ ██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║██║     ██║     █████╗
██╔═══╝   ╚██╔╝  ██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║██║     ██║     ██╔══╝
██║        ██║   ╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║╚██████╗███████╗███████╗
╚═╝        ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝╚══════╝
                """,
                id="banner"
            ),

            Static(
                "AST Powered Time-Travel Debugger",
                id="subtitle"
            ),

            Static(
                "\nWelcome to PyChronicle\n",
                id="welcome"
            ),

            Static(
                "Future Features\n"
                "• Execute Python Programs\n"
                "• Capture Runtime Variables\n"
                "• Time Travel Debugging\n"
                "• Timeline Navigation\n"
                "• Variable Inspector\n"
                "• SQLite Event History\n",
                id="features"
            ),

            Static(
                "Week 2 UI Scaffold Complete",
                id="status"
            ),

            id="main_container"
        )

        yield Footer()


if __name__ == "__main__":
    PyChronicleApp().run()
