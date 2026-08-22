import os
from textual.widgets import Static
from rich.syntax import Syntax


class CodeViewer(Static):
    """
    Handles reading the target file and displaying code
    with the currently executing line highlighted.

    Uses Rich's Syntax widget with the 'one-dark' theme for
    a professional dark-IDE appearance. Line numbers are always
    shown. The highlighted line is visually distinct via Rich's
    native highlight_lines support. Scrollable within container.
    """

    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.source_code = self._load_source()

    def _load_source(self) -> str:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()

        return f"# Error: Target script '{self.file_path}' not found."

    def highlight_line(self, line_number: int):
        """Re-render the source with line highlighted and scroll parent container into view."""
        syntax = Syntax(
            self.source_code,
            "python",
            theme="one-dark",
            line_numbers=True,
            highlight_lines={line_number},
            indent_guides=True,
            word_wrap=False,
        )
        self.update(syntax)
        try:
            # Scroll parent ScrollableContainer to keep active executing line visible
            if self.parent and hasattr(self.parent, "scroll_to"):
                self.parent.scroll_to(y=max(0, line_number - 3), animate=False)
        except Exception:
            pass