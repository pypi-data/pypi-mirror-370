from typing import Any, Optional

from rich.console import Console


class Echo:
    def __init__(self):
        self.console = Console()

    def print(self, *msgs: Any, style: Optional[str] = None):
        self.console.print(*msgs, style=style, sep="\n")

    def success(self, *msgs: Any):
        self.print(*msgs, style="bold green")

    def warning(self, *msgs: Any):
        self.print(*msgs, style="bold yellow")

    def error(self, *msgs: Any):
        self.print(*msgs, style="bold red")

    def info(self, *msgs: Any):
        self.print(*msgs, style="bold blue")


echo = Echo()
