from typing import Any, List, Optional


class OutputCallBack:
    def print_header(self, line: Any) -> None:
        print(line)

    def _print_separator(self) -> None:
        print("-" * 80)

    def print_line(self, line: str) -> None:
        print(line)

    def print_lines_in_panel(
        self, lines: List[str], header: Optional[str] = None
    ) -> None:
        self.print_header(header)
        self._print_separator()
        for line in lines:
            self.print_line(line)
        self._print_separator()

    def print_code_in_panel(
        self, lines: List[str], header: Optional[str] = None
    ) -> None:
        self.print_lines_in_panel(lines, header)

    def print(self, line: Any) -> None:
        # just an alias
        self.print_line(line)
