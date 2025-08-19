
from contextlib import contextmanager

from rich.console import Console
from rich.theme import Theme

theme = Theme({"repr.str": "none", "repr.number": "none"})

console = Console(theme=theme)
err_console = Console(stderr=True, style="bold red")


@contextmanager
def show_loading_status(message: str = "Processing... Please wait...", spinner: str = "line"):
    with console.status(f"[blue]{message}[/blue]", spinner=spinner):
        yield
