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
    for key, value in constants.TEXT_MODEL_GEN_PARAM_MAP.items():
        if key == "max_tokens" and not include_max_tokens:
            continue

        real_name: str | None = value[shared.text_model_interface.settings_section]

        if real_name is not None:
            gen_params[real_name] = settings.get(f"lm_backend/gen/{key}")
    gen_params["stream"] = settings.get("lm_backend/gen/response_stream") in ["sse", "typewriter"]
    return gen_params


def __get_port(default_port: int) -> int:
    port: int = settings.get("lm_backend/port")
    return port if port != -1 else default_port
