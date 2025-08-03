import re

from modules.core.types import MessageList
from modules import global_vars
from .interfaces import TextModelInterface, LlamaServerInterface


class MessageHistory:
    def __init__(self) -> None:
        self.__list: MessageList = []

    def add(self, role: str, content: str) -> bool:
        if role not in ["system", "user", "assistant"]:
            raise ValueError

        if role == "user" and content.rstrip() == "":
            return False

        self.__list.append({
            "role": role,
            "content": content,
        })
        return True

    def get(self) -> MessageList:
        return self.__list


def init_interface(interface: str) -> None:
    if type(global_vars.text_model_interface) == TextModelInterface:
        match interface:
            case "llama_server":
                global_vars.text_model_interface = LlamaServerInterface("http://localhost:8080")
            case _:
                raise ValueError


def refine_message(text: str, keep_thoughts: bool) -> str:
    if keep_thoughts or ("<think>" not in text and "</think>" not in text):
        return text

    text_buffer: str = ""
    for match in re.findall(r"(<think>.*?</think>\n*)(.*?)(?=<think>|$)", text, re.DOTALL):
        text_buffer += match[1]
    return text_buffer
