import pyperclip
from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg
from llmbrix.prompt import Prompt

from brixterm.ai.tools import PasteToClipboard

SYS_PROMPT = Prompt(
    "You are terminal chatbot assistant `BrixTerm`. \n\n"
    "You internally use following AI model: '{{model}}'. "
    "User is developer who can ask any kind of questions. "
    "Your answers will be printed into terminal. "
    "Make sure they are easily readable in small window. "
    "Use nice bullet points, markdown and emojis. "
    "If user asks you to write or generate something they might want to copy it with CTRL+C "
    "(e.g. code, list, SQL query, documentation, email, etc.). "
    "Always paste raw content to user's clipboard, no extra markdown tags wrapping it."
    "Always ask user for approval before you copy something to user's clipboard."
)


class ChatBot:
    def __init__(self, gpt: GptOpenAI, chat_hist_size: int = 10):
        self.agent = Agent(
            gpt=gpt,
            chat_history=ChatHistory(max_turns=chat_hist_size),
            system_msg=SystemMsg(content=SYS_PROMPT.render({"model": gpt.model})),
            tools=[PasteToClipboard()],
        )

    def chat(self, user_input: str, clipboard=False) -> str:
        if clipboard:
            user_input += f"\n\nBelow is copy of relevant context from my clipboard:\n\n{pyperclip.paste()}"
        assistant_msg = self.agent.chat(UserMsg(content=user_input))
        return "🤖💬 " + assistant_msg.content
