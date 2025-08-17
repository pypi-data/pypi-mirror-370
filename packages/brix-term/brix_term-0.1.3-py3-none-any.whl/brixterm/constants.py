# flake8: noqa: E501
DEFAULT_GPT_MODEL = "gpt-4o-mini"
CMD_HIST_SIZE = 10
CHAT_HIST_SIZE = 10
TERM_INPUT_PREFIX = (
    "\033[1;32m🤖 BxT:\033[0m"  # venv: bright green
    "\033[1;36m{}\033[0m "  # user@host: cyan
    "\033[1;34m{}\033[0m"  # cwd: blue
    "> "  # prompt symbol
)

INTRODUCTION_MSG = (
    "\n\n[bold red]🤖💥 **** Welcome to BrixTerm! ****[/bold red] 💥🤖\n\n[bold blue]Available commands:[/bold blue]\n\n"
    "[bold yellow]1. 💻 TERMINAL[/bold yellow] [bold yellow](default)[/bold yellow] - Type any "
    "[bold yellow]terminal command[/bold yellow]. If it fails then AI will suggest corrected version.\n"
    "[bold cyan]2. 👽 INTERACTIVE SHELL[/bold cyan] - Type [bold cyan]!<command>[/bold cyan] to run interactive shell. "
    "Without [bold cyan]![/bold cyan] interactive commands will timeout after 10s. E.g. try to run [bold cyan]!htop[/bold cyan]\n"
    "[bold green]3. 🐥 CODE GEN[/bold green] - Type [bold green]c <your request>[/bold green] to generate Python code. "
    "Result is automatically copied to your clipboard.\n"
    "[bold bright_green]4. 👶 CODE GEN + CLIPBOARD[/bold bright_green] - Type [bold bright_green]ccc <your request>[/bold bright_green] to generate Python code. "
    "Content of your clipboard is automatically passed to AI generator as context. Result is automatically copied back to your clipboard.\n"
    "[bold blue]5. 💬 CHAT[/bold blue] - Type [bold blue]a <your request>[/bold blue] to chat with GPT.\n"
    "[bold bright_blue]6. 🔮 CHAT + CLIPBOARD[/bold bright_blue] - Type [bold bright_blue]aaa <your request>[/bold bright_blue] to chat with GPT. "
    "Content of your clipboard is automatically pasted to the chatbot prompt as a context.\n"
    "[bold purple]7. 🏃💨️ EXIT[/bold purple] - Type [bold purple]q[/bold purple] to exit.\n\n"
)
PHOENIX_HOST = "localhost"
PHOENIX_PORT = "4317"
