from typing import Any
import re

from modules.core.types import MessageList
from modules.core import constants
from modules.core import settings
from modules import shared
from .interfaces import LlamaInterface, LlamaServerInterface


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


def init_interface(interface_name: str) -> None:
    if shared.text_model_interface is None:
        match interface_name:
            case "internal":
                shared.text_model_interface = LlamaInterface("", "internal")
            case "llama_server":
                shared.text_model_interface = LlamaServerInterface(f"http://localhost:{__get_port(8080)}", "llama_server")
            case _:
                raise ValueError


def build_gen_params(include_max_tokens: bool) -> dict[str, Any]:
    if shared.text_model_interface is None:
        return {}

    gen_params: dict[str, Any] = {}
    for n, m in constants.TEXT_MODEL_GEN_PARAM_MAP.items():
        if n == "max_tokens" and not include_max_tokens:
            continue

        if m[shared.text_model_interface.settings_section] is not None:
            gen_params[m[shared.text_model_interface.settings_section]] = settings.get(f"lm_backend/gen/{n}")  # pyright: ignore[reportArgumentType]
    gen_params["stream"] = settings.get("lm_backend/gen/response_stream") in ["sse", "typewriter"]
    return gen_params


def refine_message(text: str, keep_thoughts: bool) -> str:
    if keep_thoughts or ("<think>" not in text and "</think>" not in text):
        return text

    text_buffer: str = ""
    for match in re.findall(r"(<think>.*?</think>\n*)(.*?)(?=<think>|$)", text, re.DOTALL):
        text_buffer += match[1]
    return text_buffer


def __get_port(default_port: int) -> int:
    port: int = settings.get("lm_backend/port")
    return port if port != -1 else default_port
