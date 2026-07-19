from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from rich.syntax import Syntax


class CodeViewer(Widget):
    """
    A simple code viewer widget for PyChronicle.

    Displays syntax-highlighted Python code using Rich.
    """

    SAMPLE_CODE = """
def calculate_sum(a, b):
    total = a + b

    if total > 10:
        print("Large Number")
    else:
        print("Small Number")

    return total


x = 5
y = 8

result = calculate_sum(x, y)

print(result)
"""

    def compose(self) -> ComposeResult:

        syntax = Syntax(
            self.SAMPLE_CODE,
            "python",
            theme="monokai",
            line_numbers=True,
            word_wrap=False,
            indent_guides=True,
        )

        yield Static(syntax, id="code_display")
