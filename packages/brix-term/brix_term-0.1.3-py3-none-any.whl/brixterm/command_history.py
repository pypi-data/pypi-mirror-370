import json
from collections import deque
from subprocess import CompletedProcess


class CommandHistory:
    def __init__(self, size: int = 5, text_trim=1000):
        self.hist = deque(maxlen=size)
        self.text_trim = text_trim

    def add(self, completed_process: CompletedProcess):
        self.hist.append(completed_process)

    def to_json(self) -> str:
        serializable_cmds = [
            {
                "args": proc.args,
                "returncode": proc.returncode,
                "stdout": proc.stdout[: self.text_trim] if proc.stdout else proc.stdout,
                "stderr": proc.stderr[: self.text_trim] if proc.stderr else proc.stderr,
            }
            for proc in self.hist
        ]
        return json.dumps(serializable_cmds)
