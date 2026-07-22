import os
from textual.widgets import Static
from rich.syntax import Syntax

class CodeViewer(Static):
    """
    Handles reading the target file and displaying code tokenization blocks
    with active historical execution line highlighting.
    """
    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.source_code = self._load_source()

    def _load_source(self) -> str:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return f.read()
        return f"# Error: Target script source '{self.file_path}' not found."

    def highlight_line(self, line_number: int):
        """Re-renders text tokens to spotlight the current time-scrubbed execution frame."""
        syntax = Syntax(
            self.source_code,
            "python",
            theme="monokai",
            line_numbers=True,
            highlight_lines={line_number}
        )
        self.update(syntax)
