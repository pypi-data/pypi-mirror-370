from typing import Any, List, Optional

from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.panel import Panel
from rich.text import Text

from truefoundry.deploy.io.output_callback import OutputCallBack


def _text(line):
    return Text.from_ansi(str(line)) if "\x1b" in line else str(line)


class RichOutputCallBack(OutputCallBack):
    console = Console(soft_wrap=True)
    highlighter = ReprHighlighter()

    def print_header(self, line: Any) -> None:
        self.console.rule(_text(line), style="cyan")

    def print_line(self, line: Any) -> None:
        self.console.print(_text(line))

    def print_lines_in_panel(
        self, lines: List[str], header: Optional[str] = None
    ) -> None:
        self.console.print(Panel(self.highlighter("\n".join(lines)), title=header))

    def print_code_in_panel(self, lines: List[str], header: Optional[str] = None):
        self.print_lines_in_panel(lines, header)
