from typing import Any, List, Optional

from truefoundry.deploy.io.output_callback import OutputCallBack


class NoOutputCallBack(OutputCallBack):
    def print_header(self, line: Any) -> None:
        pass

    def _print_separator(self) -> None:
        pass

    def print_line(self, line: str) -> None:
        pass

    def print_lines_in_panel(
        self, lines: List[str], header: Optional[str] = None
    ) -> None:
        pass

    def print_code_in_panel(
        self, lines: List[str], header: Optional[str] = None
    ) -> None:
        pass

    def print(self, line: Any) -> None:
        pass
