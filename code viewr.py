from pathlib import Path

from rich.syntax import Syntax

from textual.app import ComposeResult
from textual.widgets import Static
from textual.widget import Widget


class CodeViewer(Widget):
    """
    Displays Python source code with syntax highlighting.
    """

    def __init__(self, file_path: str | None = None):
        super().__init__()

        self.file_path = file_path
        self.source_code = self.load_source()

    def load_source(self) -> str:
        """
        Load source code from a file.

        If the file cannot be read,
        show a friendly message.
        """

        if not self.file_path:
            return "# No file selected."

        path = Path(self.file_path)

        if not path.exists():
            return f"# File not found:\n{self.file_path}"

        try:
            return path.read_text(encoding="utf-8")

        except Exception as error:
            return f"# Error reading file\n{error}"

    def compose(self) -> ComposeResult:

        syntax = Syntax(
            self.source_code,
            "python",
            theme="monokai",
            line_numbers=True,
            indent_guides=True,
            word_wrap=False,
        )

        yield Static(syntax, id="code_display")
