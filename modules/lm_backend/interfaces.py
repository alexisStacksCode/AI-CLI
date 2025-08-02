from typing import Any
import os
import json
import time
from colorama import Fore
import requests
import llama_cpp
from modules.core.enums import PrintColors
from modules import utils

class TextModelInterface:
    def __init__(self, api_url: str):
        self._model = None
        self._api_url = api_url

    def launch(self, model_path: str) -> None:
        raise NotImplementedError

    def create_chat_completion(self, messages: list[Any], **kwargs: Any) -> Any:
        raise NotImplementedError

    def consume_chat_completion_response(self, response: Any) -> str:
        raise NotImplementedError

    def create_text_completion(self, prompt: str, **kwargs: Any) -> Any:
        raise NotImplementedError

    def consume_text_completion_response(self, response: Any) -> str:
        raise NotImplementedError

    @staticmethod
    def _needs_naming(model_path: str) -> str:
        check_model_existence = lambda: os.path.exists(model_path) and utils.helpers.get_file_extension(model_path) == ".gguf"

        if not check_model_existence():
            while True:
                model_path = input("Enter a language model path: ")
                if check_model_existence():
                    break
                utils.terminal.new_print("File does not exist nor is a recognized language model", PrintColors.ERROR)

        return model_path

    @staticmethod
    def _print_response(content: str) -> None:
        print(content, end="")

    @staticmethod
    def _print_response_chunk_sse(content: str) -> None:
        print(content, end="", flush=True)

    @staticmethod
    def _print_response_chunk_typewriter(content: str) -> None:
        for character in content:
            print(character, end="", flush=True)
            time.sleep(0.04)

class LlamaInterface(TextModelInterface):
    def launch(self, model_path: str) -> None:
        model_path = TextModelInterface._needs_naming(model_path)
        self._model = llama_cpp.Llama(model_path, n_gpu_layers=99, n_ctx=2048, n_batch=2048, n_ubatch=2048, verbose=False)

    def create_chat_completion(self, messages: list[Any], **kwargs: Any) -> Any:
        return self._model.create_chat_completion(messages, **kwargs)

    def consume_chat_completion_response(self, response: Any) -> str:
        try:
            iter(response) # Check if the response is a stream.

            content_buffer: str = ""
            for chunk in response:
                chunk_content: str = chunk["choices"][0]["delta"].get("content", "")
                content_buffer += chunk_content
                TextModelInterface._print_response_chunk_typewriter(chunk_content)
            return content_buffer
        except TypeError:
            content: str = response["choices"][0]["message"]["content"]
            TextModelInterface._print_response(content)
            return content

    def create_text_completion(self, prompt: str, **kwargs: Any) -> Any:
        return self._model.create_completion(prompt, **kwargs)

    def consume_text_completion_response(self, response: Any) -> str:
        try:
            iter(response) # Check if the response is a stream.

            content_buffer: str = ""
            for chunk in response:
                chunk_content: str = chunk["choices"][0]["text"]
                content_buffer += chunk_content
                TextModelInterface._print_response_chunk_typewriter(chunk_content)
            return content_buffer
        except TypeError:
            content: str = response["choices"][0]["text"]
            TextModelInterface._print_response(content)
            return content

class LlamaServerInterface(TextModelInterface):
    def launch(self, model_path: str) -> None:
        is_active: bool = False

        check_server = lambda: requests.get(f"{self._api_url}/health").status_code == 200

        try:
            is_active = check_server()
        except requests.exceptions.ConnectionError:
            model_path = TextModelInterface._needs_naming(model_path)

            server_path: str = f"server/llama-server.exe"
            if not os.path.exists(server_path):
                while True:
                    server_dir_path: str = utils.helpers.strip_path_quotes(input("Enter the path to llama.cpp: "))
                    server_path = f"{server_dir_path}llama-server.exe"
                    if os.path.exists(server_path):
                        break
                    utils.terminal.new_print(f"Directory does not exist or llama-server.exe is not in the directory", PrintColors.ERROR)

            arguments: str = utils.helpers.build_argument_string([
                "--keep -1",
                f"--model \"{model_path}\"",
            ])
            os.startfile(os.path.abspath(server_path), arguments=arguments)

        while True:
            if is_active:
                utils.terminal.new_print("Server is online", PrintColors.SUCCESS)
                break
            is_active = check_server()

        model_info: dict[str, Any] = requests.get(f"{self._api_url}/v1/models").json()
        print(f"{PrintColors.SUCCESS}You are served by: {PrintColors.SPECIAL}{utils.helpers.get_filename_without_extension(model_info["models"][0]["name"])}{Fore.RESET}")

    def create_chat_completion(self, messages: list[Any], **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "model": "default",
            "messages": messages,
        }
        payload.update(kwargs)
        stream: bool = payload.get("stream", False)

        response: requests.Response = requests.post(f"{self._api_url}/v1/chat/completions", json=payload, stream=stream)
        if not stream:
            return response.json()
        else:
            return response.iter_lines()

    def consume_chat_completion_response(self, response: Any) -> str:
        if type(response) == dict[str, Any]:
            content: str = response["choices"][0]["message"]["content"]
            TextModelInterface._print_response(content)
            return content
        else:
            content_buffer: str = ""
            for line in response:
                decoded_line: str = line.decode("utf-8")
                if decoded_line.startswith("data: ") and not decoded_line.endswith("[DONE]"):
                    chunk: str | None = json.loads(decoded_line[len("data: "):])["choices"][0]["delta"].get("content", "")
                    if chunk is not None:
                        content_buffer += chunk
                        TextModelInterface._print_response_chunk_typewriter(chunk)
            return content_buffer

    def create_text_completion(self, prompt: str, **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "model": "default",
            "prompt": prompt,
            "n_predict": 16,
        }
        payload.update(kwargs)
        stream: bool = payload.get("stream", False)

        response: requests.Response = requests.post(f"{self._api_url}/completion", json=payload, stream=stream)
        if not stream:
            return response.json()
        else:
            return response.iter_lines()

    def consume_text_completion_response(self, response: Any) -> str:
        if type(response) == dict:
            TextModelInterface._print_response(response["content"])
        else:
            for line in response:
                decoded_line: str = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    chunk: str = json.loads(line[len("data: "):])["content"]
                    TextModelInterface._print_response_chunk_typewriter(chunk)
