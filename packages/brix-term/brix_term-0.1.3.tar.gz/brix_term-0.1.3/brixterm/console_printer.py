from subprocess import CompletedProcess

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax


class ConsolePrinter:
    def __init__(self, dark_mode=True):
        self.dark_mode = dark_mode
        self.console = Console()

    def print(self, content: str | Markdown):
        self.console.print(content)

    def print_python(self, content: str):
        theme = "monokai" if self.dark_mode else "xcode"
        syntax = Syntax(content, "python", line_numbers=True, theme=theme, indent_guides=True)
        self.console.print(syntax)

    def print_markdown(self, content: str):
        markdown = Markdown(content)
        self.print(markdown)

    def print_subprocess_output(self, completed_process: CompletedProcess):
        if completed_process.stdout:
            self.print(f"[bold green]STDOUT:[/bold green]\n{completed_process.stdout}")
        if completed_process.stderr:
            self.print(f"[bold red]STDERR:[/bold red]\n{completed_process.stderr}")
        self.print(f"[dim]Return code: {completed_process.returncode}[/dim]")
