from typing import Any
from abc import ABC, abstractmethod
import os
import json
import random
import time

from colorama import Fore
import requests
import llama_cpp

from modules.core.types import MessageList
from modules.core.enums import PrintColors
from modules import utils


class TextModelInterface(ABC):
    def __init__(self, api_url: str, settings_section: str) -> None:
        self.settings_section: str = settings_section
        self._model: Any = None
        self._api_url: str = api_url

    @abstractmethod
    def setup(self, model_path: str, **kwargs: Any) -> None:
        pass

    def create_chat_completion(self, messages: MessageList, **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "messages": messages,
            **kwargs,
        }
        stream: bool = payload.get("stream", False)

        response: requests.Response = requests.post(f"{self._api_url}/v1/chat/completions", json=payload, stream=stream)
        return response.json() if not stream else response.iter_lines()

    def consume_chat_completion_response(self, response: Any, capture_behavior: str) -> str:
        if isinstance(response, dict):
            return TextModelInterface._capture_text(response["choices"][0]["message"]["content"], "off")  # pyright: ignore[reportUnknownArgumentType]
        else:
            text_buffer: str = ""
            for line in response:
                decoded_line: str = line.decode("utf-8")
                if decoded_line.startswith("data: ") and not decoded_line.endswith("[DONE]"):
                    text_buffer += TextModelInterface._capture_text(json.loads(decoded_line[len("data: "):])["choices"][0]["delta"].get("content", ""), capture_behavior)
            return text_buffer

    def create_text_completion(self, prompt: str, **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "prompt": prompt,
            **kwargs,
        }
        stream: bool = payload.get("stream", False)

        response: requests.Response = requests.post(f"{self._api_url}/v1/completions", json=payload, stream=stream)
        return response.json() if not stream else response.iter_lines()

    def consume_text_completion_response(self, response: Any, capture_behavior: str) -> str:
        if isinstance(response, dict):
            return TextModelInterface._capture_text(response["choices"][0]["text"], "off")  # pyright: ignore[reportUnknownArgumentType]
        else:
            text_buffer: str = ""
            for line in response:
                decoded_line: str = line.decode("utf-8")
                if decoded_line.startswith("data: ") and not decoded_line.endswith("[DONE]"):
                    text_buffer += TextModelInterface._capture_text(json.loads(decoded_line[len("data: "):])["choices"][0].get("text", ""), capture_behavior)
            return text_buffer

    @staticmethod
    def _prompt_for_model_path_if_nonexistent(model_path: str) -> str:
        check_model_existence = lambda: os.path.exists(model_path) and utils.helpers.get_file_extension(model_path) == ".gguf"

        if not check_model_existence():
            while True:
                model_path = input("Enter a language model path: ")
                if check_model_existence():
                    break
                utils.terminal.new_print("File does not exist nor is a recognized language model", PrintColors.ERROR)

        return model_path

    @staticmethod
    def _capture_text(text: str | None, print_behavior: str) -> str:
        if text is not None:
            match print_behavior:
                case "off":
                    print(text, end="")
                case "sse":
                    print(text, end="", flush=True)
                case "typewriter":
                    for character in text:
                        print(character, end="", flush=True)
                        time.sleep(0.04)
                case _:
                    raise ValueError
            return text
        return ""


class LlamaInterface(TextModelInterface):
    def setup(self, model_path: str, **kwargs: Any) -> None:
        model_path = TextModelInterface._prompt_for_model_path_if_nonexistent(model_path)
        self._model = llama_cpp.Llama(
            model_path,
            n_gpu_layers=kwargs.get("gpu_layers", 999),
            use_mmap=kwargs.get("use_mmap", False),
            use_mlock=kwargs.get("use_mlock", False),
            n_ctx=kwargs.get("context_size", 8192),
            n_batch=kwargs.get("logical_batch_size", 2048),
            n_ubatch=kwargs.get("physical_batch_size", 2048),
            offload_kqv=kwargs.get("kv_uses_gpu", True),
            flash_attn=kwargs.get("use_flash_attention", True),
            swa_full=kwargs.get("use_full_swa_cache", False),
            verbose=False,
        )

    def create_chat_completion(self, messages: MessageList, **kwargs: Any) -> Any:
        kwargs["seed"] = LlamaInterface.__get_random_seed()

        return self._model.create_chat_completion(messages, **kwargs)

    def consume_chat_completion_response(self, response: Any, capture_behavior: str) -> str:
        try:
            # Check if the response is a stream.
            iter(response)

            text_buffer: str = ""
            for chunk_text in response:
                text_buffer += TextModelInterface._capture_text(chunk_text["choices"][0]["delta"].get("content", ""), capture_behavior)
            return text_buffer
        except TypeError:
            return TextModelInterface._capture_text(response["choices"][0]["message"]["content"], "off")

    def create_text_completion(self, prompt: str, **kwargs: Any) -> Any:
        kwargs["seed"] = LlamaInterface.__get_random_seed()

        return self._model.create_completion(prompt, **kwargs)

    def consume_text_completion_response(self, response: Any, capture_behavior: str) -> str:
        try:
            # Check if the response is a stream.
            iter(response)

            text_buffer: str = ""
            for chunk_text in response:
                text_buffer += TextModelInterface._capture_text(chunk_text["choices"][0]["text"], capture_behavior)
            return text_buffer
        except TypeError:
            return TextModelInterface._capture_text(response["choices"][0]["text"], "off")

    @staticmethod
    def __get_random_seed() -> int:
        # As of llama-cpp-python v0.3.14, random seeds don't work properly.
        return random.randint(0, 2 ** 32)


class LlamaServerInterface(TextModelInterface):
    def setup(self, model_path: str, **kwargs: Any) -> None:
        is_active: bool = False

        check_server = lambda: requests.get(f"{self._api_url}/health").status_code == 200

        try:
            is_active = check_server()
        except requests.exceptions.ConnectionError:
            model_path = TextModelInterface._prompt_for_model_path_if_nonexistent(model_path)
            model_mmproj_path: str = f"{utils.helpers.get_filename_without_extension(model_path)}-mmproj.gguf"
            if not os.path.exists(model_mmproj_path):
                model_mmproj_path = ""

            server_path: str = f"servers/llama.cpp/llama-server.exe"
            if not os.path.exists(server_path):
                while True:
                    server_dir_path: str = utils.helpers.strip_path_quotes(input("Enter the path to llama.cpp: "))
                    server_path = f"{server_dir_path}llama-server.exe"
                    if os.path.exists(server_path):
                        break
                    utils.terminal.new_print(f"Directory does not exist or llama-server.exe is not in the directory", PrintColors.ERROR)

            arguments: str = utils.helpers.build_argument_string([
                "--no-webui",
                f"--gpu-layers {kwargs.get("gpu_layers", 999)}",
                "--no-mmproj-offload" if not kwargs.get("mmproj_uses_gpu", True) and model_mmproj_path != "" else "",
                "--no-kv-offload" if not kwargs.get("kv_uses_gpu", True) else "",
                "--no-mmap" if not kwargs.get("use_mmap", False) else "",
                "--mlock" if kwargs.get("use_mlock", False) else "",
                "--flash-attn" if kwargs.get("use_flash_attention", True) else "",
                "--swa-full" if kwargs.get("use_full_swa_cache", False) else "",
                "--kv-unified" if kwargs.get("use_unified_kv_buffer", False) else "",
                f"--cache-reuse {kwargs.get("kv_cache_reuse_size", 256)}",
                "--cont-batching" if kwargs.get("use_continuous_batching", True) else "--no-cont-batching",
                f"--batch-size {kwargs.get("logical_batch_size", 2048)}",
                f"--ubatch-size {kwargs.get("physical_batch_size", 2048)}",
                "--no-context-shift" if not kwargs.get("use_context_shift", True) else "",
                f"--ctx-size {kwargs.get("context_size", 8192)}",
                "--keep -1",
                f"--model \"{model_path}\"",
                f"--mmproj \"{model_mmproj_path}\"" if model_mmproj_path != "" else "",
            ])
            os.startfile(os.path.abspath(server_path), arguments=arguments)

        while True:
            if is_active:
                utils.terminal.new_print("Server is online", PrintColors.SUCCESS)
                break
            is_active = check_server()

        model_info: dict[str, Any] = requests.get(f"{self._api_url}/v1/models").json()
        print(f"{PrintColors.SUCCESS}You are served by: {PrintColors.SPECIAL}{utils.helpers.get_filename_without_extension(model_info["models"][0]["name"])}{Fore.RESET}")
