"""
launch_screen.py — PyChronicle script-selection launch screen.

Provides LaunchApp, a standalone Textual App that presents a centered
welcome screen. After the user confirms a valid .py path,
self.selected_script is set and the app exits so the caller can
launch PyChronicleUI with the chosen script.
"""
import os

from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal


class LaunchApp(App):
    """
    Standalone script-selection screen.

    Usage
    -----
        launch = LaunchApp()
        launch.run()
        script = launch.selected_script   # None if user cancelled
    """

    CSS = """
    Screen {
        background: #0d1117;
        align: center middle;
    }

    #launch-card {
        width: 68;
        background: #161b22;
        border: solid #21262d;
        border-top: tall #58a6ff;
        padding: 2 4;
    }

    #brand-title {
        color: #58a6ff;
        text-style: bold;
        text-align: center;
        content-align: center middle;
        height: 2;
    }

    #brand-sub {
        color: #c9d1d9;
        text-style: bold;
        text-align: center;
        content-align: center middle;
        height: 1;
    }

    #brand-desc {
        color: #8b949e;
        text-align: center;
        content-align: center middle;
        height: 1;
        margin-bottom: 1;
    }

    #feature-tagline {
        color: #58a6ff;
        text-align: center;
        content-align: center middle;
        height: 1;
        margin-bottom: 1;
    }

    #brand-hr {
        color: #21262d;
        text-align: center;
        content-align: center middle;
        height: 1;
        margin-bottom: 1;
    }

    #input-label {
        color: #e3b341;
        text-style: bold;
        height: 1;
        margin-bottom: 0;
    }

    #script-input {
        border: solid #30363d;
        background: #0d1117;
        color: #c9d1d9;
        margin-bottom: 1;
    }

    #script-input:focus {
        border: solid #58a6ff;
    }

    #preset-row {
        height: 3;
        align: center middle;
        margin-bottom: 1;
    }

    #preset-btn {
        width: 100%;
        background: #1c2128;
        color: #8b949e;
        border: solid #30363d;
    }

    #preset-btn:hover {
        background: #21262d;
        color: #58a6ff;
        border: solid #58a6ff;
    }

    #error-msg {
        color: #f85149;
        height: 1;
        margin-bottom: 0;
    }

    #launch-btn {
        width: 100%;
        background: #0f2a3a;
        color: #58a6ff;
        border: solid #1f6feb;
        text-style: bold;
        margin-top: 1;
    }

    #launch-btn:hover {
        background: #1f6feb;
        color: #ffffff;
        border: solid #388bfd;
    }

    #hint-text {
        color: #6e7681;
        text-align: center;
        content-align: center middle;
        height: 1;
        margin-top: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, default_path: str = "", **kwargs):
        super().__init__(**kwargs)
        self.selected_script: str | None = None
        self._default_path = default_path

    def compose(self) -> ComposeResult:
        with Vertical(id="launch-card"):
            yield Static("PyChronicle", id="brand-title")
            yield Static("AST-Powered Time-Travel Debugger", id="brand-sub")
            yield Static("Analyze and explore your Python program step-by-step.", id="brand-desc")
            yield Static("AST Analysis • Runtime Tracing • Variable Tracking • Time Travel", id="feature-tagline")
            yield Static("─" * 60, id="brand-hr")
            yield Static("Python Script Target", id="input-label")
            yield Input(
                value=self._default_path,
                placeholder="Enter path (e.g. examples/sample_script.py)",
                id="script-input",
            )
            with Horizontal(id="preset-row"):
                yield Button("Use Sample Script (examples/sample_script.py)", id="preset-btn", variant="default")
            yield Static("", id="error-msg")
            yield Button("  Analyze & Debug", id="launch-btn", variant="primary")
            yield Static("Enter to confirm  ·  Esc to cancel", id="hint-text")

    def on_mount(self) -> None:
        self.title = "PyChronicle"
        self.sub_title = "AST-Powered Time-Travel Debugger"
        self.query_one("#script-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "launch-btn":
            self._confirm()
        elif event.button.id == "preset-btn":
            inp = self.query_one("#script-input", Input)
            inp.value = "examples/sample_script.py"
            self._confirm()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._confirm()

    def _confirm(self) -> None:
        path = self.query_one("#script-input", Input).value.strip()
        err = self.query_one("#error-msg", Static)

        if not path:
            err.update("  Enter a script path to continue")
            return
        if not path.endswith(".py"):
            err.update("  File must have a .py extension")
            return
        if not os.path.exists(path):
            err.update(f"  File not found: {path}")
            return

        self.selected_script = path
        self.exit()

    def action_cancel(self) -> None:
        """Exit without selecting a script."""
        self.exit()
