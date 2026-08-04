import os
from textual.widgets import Static
from rich.syntax import Syntax

class CodeViewer(Static):
    """Renders Python source code and highlights the active execution frame."""
    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.source_code = self._load_source()

    def _load_source(self) -> str:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        return f"# Error: Source target file '{self.file_path}' unreadable."

    def highlight_line(self, line_number: int):
        """Highlights the time-scrubbed execution frame line and auto-scrolls."""
        syntax = Syntax(
            self.source_code,
            "python",
            theme="monokai",
            line_numbers=True,
            highlight_lines={line_number}
        )
        self.update(syntax)
        # Scroll target line into focus
        self.scroll_to_region((0, max(0, line_number - 3), 100, line_number + 3), animate=False)
