from types import FunctionType
from typing import Any
import os

from modules.core.enums import PrintColors
from modules import utils, lm_backend, im_backend
from modules import shared
from modules.core import settings


def _mode_chat() -> None:
    message_history: lm_backend.MessageHistory = lm_backend.MessageHistory()

    if os.path.exists("data/chat_system_prompt.txt"):
        try:
            with open("data/chat_system_prompt.txt", "rt") as file:
                message_history.add("system", file.read())
        except UnicodeDecodeError:
            utils.terminal.new_print("Malformed system prompt file", PrintColors.WARNING)
    while True:
        if shared.text_model_interface is None:
            exit()

        user_message: str = input(utils.terminal.colorize_text("\nUSER: ", PrintColors.USER_TURN))
        if message_history.add("user", user_message):
            utils.terminal.new_print("\nMODEL: ", PrintColors.MODEL_TURN, "")
            response: Any = shared.text_model_interface.create_chat_completion(message_history.get(), **lm_backend.build_gen_params(False))
            model_message: str = shared.text_model_interface.consume_chat_completion_response(response, settings.get("lm_backend/gen/response_stream"))
            message_history.add("assistant", model_message)
            print("\n", end="")
        else:
            utils.terminal.new_print("Cannot send empty messages", PrintColors.ERROR)


def _mode_autocomplete() -> None:
    while True:
        if shared.text_model_interface is None:
            exit()

        prompt: str = input(utils.terminal.colorize_text("\n> ", PrintColors.USER_TURN))
        print(f"{PrintColors.MODEL_TURN}{prompt}", end="", flush=True)
        response: Any = shared.text_model_interface.create_text_completion(prompt, **lm_backend.build_gen_params(True))
        shared.text_model_interface.consume_text_completion_response(response, settings.get("lm_backend/gen/response_stream"))
        print("\n", end="")


MODES: dict[str, FunctionType] = {
    "chat": _mode_chat,
    "autocomplete": _mode_autocomplete,
}
