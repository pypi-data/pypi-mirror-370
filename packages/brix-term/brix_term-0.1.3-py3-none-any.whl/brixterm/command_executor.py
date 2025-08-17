import os
from subprocess import CompletedProcess, TimeoutExpired, run


class CommandExecutor:
    def __init__(self, shell_cmd_timeout=10):
        self.shell_cmd_timeout = shell_cmd_timeout

    def execute_shell_cmd(self, cmd: str) -> CompletedProcess:
        try:
            return run(cmd, shell=True, text=True, capture_output=True, timeout=self.shell_cmd_timeout)
        except TimeoutExpired:
            return CompletedProcess(
                cmd,
                returncode=124,
                stdout="",
                stderr="Command timed out. " "If the app is interactive run with ! prefix (e.g. !htop).\n",
            )
        except Exception as e:
            return CompletedProcess(cmd, returncode=1, stdout="", stderr=f"Execution error: {e}\n")

    @staticmethod
    def execute_interactive_shell_cmd(cmd: str):
        try:
            return run(cmd, shell=True, text=True, capture_output=False)
        except Exception as e:
            return CompletedProcess(cmd, returncode=1, stdout="", stderr=f"Execution error: {e}\n")

    @staticmethod
    def execute_cd_cmd(cmd: str) -> tuple[str, str]:
        path_arg = cmd[3:].strip()
        target_path = os.path.abspath(os.path.expanduser(path_arg))

        os.chdir(target_path)
        cwd = os.getcwd()

        logical_cwd = os.path.normpath(os.path.expanduser(path_arg))
        if not os.path.isabs(logical_cwd):
            logical_cwd = os.path.abspath(logical_cwd)

        return cwd, logical_cwd
