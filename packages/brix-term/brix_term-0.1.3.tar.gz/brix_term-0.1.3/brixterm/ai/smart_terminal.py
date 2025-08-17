from subprocess import CompletedProcess

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg
from llmbrix.prompt import Prompt
from llmbrix.tools import ListDir
from pydantic import BaseModel, Field

from brixterm.command_executor import CommandExecutor
from brixterm.command_history import CommandHistory
from brixterm.console_context import ConsoleContext
from brixterm.console_printer import ConsolePrinter
from brixterm.constants import INTRODUCTION_MSG

SYS_PROMPT = (
    "You are running in special unix terminal. "
    "In this terminal user will type a command. If command is incorrect (typo, mistake) it will fail failed. "
    "Your task is to suggest corrected unix command that would work for the user."
)

USER_PROMPT = Prompt(
    """
    # Command typed by user

        ```bash
        {{cmd}}
        ```

    # Outputs from attempted command execution

    ## Stdout
        ```text
            {{stdout}}
        ```

    ## Stderr
        ```text
        {{stderr}}
        ```

    ## Return code

        ```text
        {{return_code}}
        ```

    # Additional information

    ## User name

        ```text
        {{user}}
        ```

    ## Current working dir

        ```text
        {{cwd}}
        ```

    ## List of files in current dir

        ```text
        {{list_dir}}
        ```
    ## History of commands user ran so far

        ```json
        {{cmd_hist}}
        ```

    ## Terminal introduction message explaining special commands additionally available in this terminal:

        ```text
        {{intro}}
        ```
    """
)


class TerminalCommand(BaseModel):
    explanation: str = Field(
        ..., description="Very short 1 sentence explanation for the suggestion. Talk directly to user. Include emojis."
    )
    terminal_command: str = Field(
        ..., description="A valid Unix command string that can be directly executed in the shell"
    )


class SmartTerminal:
    def __init__(
        self,
        gpt: GptOpenAI,
        command_executor: CommandExecutor,
        console_printer: ConsolePrinter,
        command_history: CommandHistory,
        max_tool_call_iter=5,
        chat_max_turns=10,
    ):
        self.command_executor = command_executor
        self.console_printer = console_printer
        self.command_history = command_history
        self.terminal_agent = Agent(
            gpt=gpt,
            chat_history=ChatHistory(max_turns=chat_max_turns),
            system_msg=SystemMsg(content=SYS_PROMPT),
            tools=[ListDir()],
            output_format=TerminalCommand,
            max_tool_call_iter=max_tool_call_iter,
        )

    def _run_and_print(self, cmd):
        completed_process = self.command_executor.execute_shell_cmd(cmd)
        self.console_printer.print_subprocess_output(completed_process)
        self.command_history.add(completed_process)
        return completed_process

    def _suggest_command(self, cmd: str, completed_process: CompletedProcess, ctx: ConsoleContext):
        user_msg = USER_PROMPT.render(
            {
                "cmd": cmd,
                "stdout": completed_process.stdout,
                "stderr": completed_process.stderr,
                "return_code": completed_process.returncode,
                "cwd": ctx.cwd,
                "user": ctx.user,
                "list_dir": ctx.list_dir,
                "cmd_hist": ctx.cmd_hist,
                "intro": INTRODUCTION_MSG,
            }
        )
        response = self.terminal_agent.chat(UserMsg(content=user_msg))
        return response.content_parsed.terminal_command, response.content_parsed.explanation

    def run(self, cmd: str, ctx: ConsoleContext):
        completed_process = self._run_and_print(cmd)
        if completed_process.returncode != 0:
            suggested_cmd, explanation = self._suggest_command(cmd=cmd, completed_process=completed_process, ctx=ctx)
            if suggested_cmd:
                self.console_printer.print("\n⚠️ [bold red]Command failed.[/bold red]")
                self.console_printer.print(f"💡 [bold green]{explanation}[/bold green]")
                self.console_printer.print(
                    f"🧠 [bold blue]Suggested fix:[/bold blue]\n  [bold red]{suggested_cmd}[/bold red]"
                )
                self.console_printer.print(
                    "\n[cyan]Do you want to run the[/cyan] [bold red]suggested command?[/bold red]"
                )
                user_input = input("  [y ✅  / N ❌ /  💬 feedback]: ").strip()

                if user_input.strip().lower() == "y":
                    return suggested_cmd
                elif user_input.strip().lower() != "n":
                    return user_input
