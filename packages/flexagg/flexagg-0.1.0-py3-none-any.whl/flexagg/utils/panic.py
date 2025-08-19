from typing import Optional

import typer
from rich.console import Console
from rich.text import Text
from typing_extensions import Never


def panic(*msg: str, details: Optional[str] = None, exit_code: int = -1) -> Never:
    """
    统一异常退出方法，使用rich.console输出错误信息

    Args:
        msg: 主要错误消息
        details: 详细错误信息（可选）
        exit_code: 退出码，默认为-1
    """
    console = Console(stderr=True)

    # 输出主要错误消息
    s = "\n".join(msg)
    error_text = Text(f"[PANIC] {s}", style="bold red")
    console.print(error_text)

    # 输出详细错误信息
    if details:
        details_text = Text(f"{details}", style="yellow")
        console.print(details_text)

    raise typer.Exit(exit_code)
