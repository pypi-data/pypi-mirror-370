import getpass
import os
import readline  # noqa: F401
import socket
from subprocess import CompletedProcess

from brixterm.ai import ChatBot, CodeGenerator, SmartTerminal
from brixterm.command_executor import CommandExecutor
from brixterm.command_history import CommandHistory
from brixterm.console_context import ConsoleContext
from brixterm.console_printer import ConsolePrinter
from brixterm.constants import INTRODUCTION_MSG, TERM_INPUT_PREFIX


class TerminalApp:
    def __init__(
        self,
        console_printer: ConsolePrinter,
        command_executor: CommandExecutor,
        smart_terminal: SmartTerminal,
        chatbot: ChatBot,
        code_generator: CodeGenerator,
        command_history: CommandHistory,
    ):
        self.smart_terminal = smart_terminal
        self.chatbot = chatbot
        self.code_generator = code_generator
        self.console_printer = console_printer
        self.command_executor = command_executor
        self.cwd = os.getcwd()
        self.logical_cwd = os.environ.get("PWD", self.cwd)
        self.command_history = command_history

    @staticmethod
    def get_logical_cwd_name(cwd: str) -> str:
        path = os.path.abspath(cwd)
        base = os.path.basename(path)
        parent = os.path.dirname(path)
        if parent == "/":
            return f"/{base}"
        return base

    def get_context(self) -> ConsoleContext:
        venv = os.environ.get("VIRTUAL_ENV")
        venv = f"({os.path.basename(venv)})" if venv else ""
        user = getpass.getuser()
        host = socket.gethostname()
        cwd_name = self.get_logical_cwd_name(self.logical_cwd)
        list_dir = self.command_executor.execute_shell_cmd("ls -a").stdout
        cmd_hist = self.command_history.to_json()
        if list_dir:
            list_dir = list_dir[:1000]
        return ConsoleContext(
            cwd=self.cwd, cwd_name=cwd_name, user=user, host=host, venv=venv, list_dir=list_dir, cmd_hist=cmd_hist
        )

    def read_input(self) -> tuple[str, ConsoleContext]:
        ctx = self.get_context()
        content = TERM_INPUT_PREFIX.format(ctx.venv, ctx.cwd_name)
        cmd = input(content).strip()
        return cmd, ctx

    def run(self):
        cmd = None
        self.console_printer.print(INTRODUCTION_MSG)
        while True:
            try:
                if not cmd:
                    cmd, ctx = self.read_input()
                else:
                    ctx = self.get_context()

                if cmd.lower() in ("exit", "e", "quit", "q"):
                    cmd = None
                    break
                elif cmd.startswith("!"):
                    completed_process = self.command_executor.execute_interactive_shell_cmd(cmd[1:])
                    self.command_history.add(completed_process)
                    cmd = None

                elif cmd.startswith("cd "):
                    try:
                        self.cwd, self.logical_cwd = self.command_executor.execute_cd_cmd(cmd)
                        self.command_history.add(CompletedProcess(args=cmd, returncode=0))
                        cmd = None
                    except Exception:
                        cmd = self.smart_terminal.run(cmd, ctx)
                elif cmd == "clear":
                    os.system("cls" if os.name == "nt" else "clear")
                    cmd = None
                else:
                    cmd_name = cmd.split(" ")[0].strip()
                    cmd_content = " ".join(cmd.split(" ")[1:])

                    if cmd_name == "a" or cmd_name == "aaa":
                        self.console_printer.print("🤖💬 Typing...")
                        answer = self.chatbot.chat(cmd_content, clipboard=cmd_name == "aaa")
                        self.console_printer.print_markdown(answer)
                        cmd = None
                        continue
                    elif cmd_name == "c" or cmd_name == "ccc":
                        self.code_generator.generate_and_print(cmd_content, clipboard=cmd_name == "ccc")
                        cmd = None
                        continue
                    else:
                        cmd = self.smart_terminal.run(cmd, ctx)
            except KeyboardInterrupt:
                self.console_printer.print("\n(Interrupted)")
                cmd = None
