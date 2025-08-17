import pyperclip
from llmbrix.tool import Tool, ToolOutput, ToolParam

NAME = "paste_to_users_clipboard"
DESC = "Takes provided content and pastes it to users clipboard, equivalent to CTRL+C."
PARAM = ToolParam(name="content_to_copy", desc="This content will be copied to users clipboard.", dtype=str)


class PasteToClipboard(Tool):
    def __init__(self):
        super().__init__(name=NAME, desc=DESC, params=[PARAM])

    def exec(self, content_to_copy: str) -> ToolOutput:
        pyperclip.copy(content_to_copy)
        return ToolOutput(content="Successfully copied content to user's clipboard.")
