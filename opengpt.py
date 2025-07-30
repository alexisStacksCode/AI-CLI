from typing import Any
import opengpt_constants
import opengpt_utils
import opengpt_networking
import os
import subprocess
import json
import base64
import re
import datetime
import time
import requests

if __name__ == "__main__":
    settings: dict[str, Any] = {
        "mode": "chat",
        "server_init_settings": {
            "startup_behavior": "separate_process",
            "disable_mmproj": False,
            "use_mmap": True,
            "use_mlock": False,
            "gpu_layers": -1,
            "mmproj_uses_gpu": True,
            "kv_uses_gpu": True,
            "use_flash_attention": True,
            "use_full_swa_cache": False,
            "use_continuous_batching": True,
            "logical_max_batch_size": 2048,
            "physical_max_batch_size": 2048,
            "use_unified_kv_buffer": False,
            "kv_cache_data_type_k": "f16",
            "kv_cache_data_type_v": "f16",
            "kv_cache_defragmentation_threshold": 0.1,
            "kv_cache_reuse_size": 256,
            "context_size": 8192,
        },
        "text_model_settings": {
            "port": 9001,
            "response_stream": "sse",
            "chat_show_thoughts_in_nonstreamed_responses": True,
            "chat_include_thoughts_in_context": False,
            "autocomplete_max_tokens": 128,
            # TODO: implement generation parameters
        },
        "image_model_settings": {
            "api_type": "sd_webui",
            "port": -1,
            "open_output_on_gen": False,
        },
    }
    llama_server_url: str = "http://localhost:"
    is_llama_server_online: bool = False
    text_model_id: str = ""
    text_model_modalities: dict[str, Any] = {}
    text_model_chat_message_history: list[dict[str, Any]] = []
    image_gen_server_url: str = "http://localhost:"

    def error_and_exit(error_message: str) -> None:
        opengpt_utils.new_print(error_message, opengpt_constants.PRINT_COLORS["error"])
        time.sleep(3.0)
        exit()

    # noinspection PyShadowingNames
    def append_message(role: str, content: str, attachment_path: str = "") -> bool:
        if role not in opengpt_constants.TEXT_MODEL_CHAT_ROLES:
            opengpt_utils.new_print(f"Cannot add messages from role '{role}' to the context", opengpt_constants.PRINT_COLORS["error"])
            return False

        attachment_name: str = os.path.basename(attachment_path)
        attachment_extension: str = opengpt_utils.get_file_extension(attachment_name)

        if attachment_name in opengpt_constants.TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES or attachment_extension in opengpt_constants.TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS:
            pass

        if role == "user" and content.strip() == "":
            return False

        text_model_chat_message_history.append({
            "role": role,
            "content": content,
        })
        return True

    # noinspection PyShadowingNames
    def refine_message(content: str, keep_thoughts: bool) -> str:
        if keep_thoughts or ("<think>" not in content and "</think>" not in content):
            return content

        content_buffer: str = ""
        for match in re.findall(r"(<think>.*?</think>\n*)(.*?)(?=<think>|$)", content, re.DOTALL):
            content_buffer += match[1]
        return content_buffer

    if os.path.exists(opengpt_constants.SETTINGS_PATH):
        try:
            with open(opengpt_constants.SETTINGS_PATH, "rt") as file:
                new_settings: dict[Any, Any] = json.load(file)

                for key, value in settings.items():
                    if key in new_settings:
                        settings[key] = new_settings[key]
        except json.JSONDecodeError:
            opengpt_utils.new_print("Malformed settings file", opengpt_constants.PRINT_COLORS["warning"])
    with open(opengpt_constants.SETTINGS_PATH, "wt") as file:
        json.dump(settings, file, indent=4)

    llama_server_url += str(settings["text_model_settings"]["port"])
    if settings["image_model_settings"]["api_type"] == "internal":
        try:
            import stable_diffusion_cpp # type: ignore
        except ImportError:
            error_and_exit("image_model_settings.api_type is set to 'internal' but Python module 'stable-diffusion-cpp-python' is not installed")
    if settings["image_model_settings"]["port"] == -1:
        match settings["image_model_settings"]["api_type"]:
            case "internal":
                pass
            case "sd_webui":
                image_gen_server_url += "7860"
            case "swarmui":
                image_gen_server_url += "7801"
            case "koboldcpp":
                image_gen_server_url += "5001"
            case _:
                error_and_exit("Failed to initialize image_gen_server_url with default port")
    else:
        image_gen_server_url += str(settings["image_model_settings"]["port"])

    try:
        is_llama_server_online = opengpt_networking.get_llama_server_status(llama_server_url)
        if is_llama_server_online:
            opengpt_utils.new_print("Server is online", opengpt_constants.PRINT_COLORS["success"])
    except requests.exceptions.ConnectionError:
        llama_server_path: str = f"llama.cpp/{opengpt_constants.SERVER_FILENAME}"
        if not os.path.exists(llama_server_path):
            while True:
                llama_cpp_dir_path: str = opengpt_utils.strip_path_quotes(input("Enter the path to llama.cpp: "))
                llama_server_path = f"{llama_cpp_dir_path}{opengpt_constants.SERVER_FILENAME}"
                if not os.path.exists(llama_server_path):
                    opengpt_utils.new_print(f"Directory does not exist or {opengpt_constants.SERVER_FILENAME} is not in the directory", opengpt_constants.PRINT_COLORS["error"])
                    continue
                break

        while True:
            text_model_path: str = opengpt_utils.strip_path_quotes(input("Enter a language model path: "))
            if not opengpt_utils.is_valid_text_model(text_model_path):
                opengpt_utils.new_print("File does not exist nor is a valid language model", opengpt_constants.PRINT_COLORS["error"])
                continue
            text_model_mmproj_path: str = f"{text_model_path.removesuffix(".gguf")}-mmproj.gguf"
            if settings["server_init_settings"]["disable_mmproj"] or not os.path.exists(text_model_mmproj_path):
                text_model_mmproj_path = ""
            arguments: str = opengpt_utils.build_arguments([
                "--no-webui",
                f"--port {settings["text_model_settings"]["port"]}",
                "--no-mmap" if not settings["server_init_settings"]["use_mmap"] else "",
                "--mlock" if settings["server_init_settings"]["use_mlock"] else "",
                f"--gpu-layers {opengpt_utils.calculate_gpu_layers_for_text_model(text_model_path, text_model_mmproj_path) if settings["server_init_settings"]["gpu_layers"] == -1 else settings["server_init_settings"]["gpu_layers"]}",
                "--no-mmproj-offload" if text_model_mmproj_path != "" and not settings["server_init_settings"]["mmproj_uses_gpu"] else "",
                "--no-kv-offload" if not settings["server_init_settings"]["kv_uses_gpu"] else "",
                "--flash-attn" if settings["server_init_settings"]["use_flash_attention"] else "",
                "--swa-full" if settings["server_init_settings"]["use_full_swa_cache"] else "",
                "--cont-batching" if settings["server_init_settings"]["use_continuous_batching"] else "--no-cont-batching",
                f"--batch-size {settings["server_init_settings"]["logical_max_batch_size"]}",
                f"--ubatch-size {settings["server_init_settings"]["physical_max_batch_size"]}",
                "--kv-unified" if settings["server_init_settings"]["use_unified_kv_buffer"] else "",
                f"--cache-type-k {settings["server_init_settings"]["kv_cache_data_type_k"]}",
                f"--cache-type-v {settings["server_init_settings"]["kv_cache_data_type_v"]}",
                f"--defrag-thold {settings["server_init_settings"]["kv_cache_defragmentation_threshold"]}",
                f"--cache-reuse {settings["server_init_settings"]["kv_cache_reuse_size"]}",
                "--no-context-shift" if not settings["server_init_settings"]["use_context_shift"] else "",
                f"--ctx-size {settings["server_init_settings"]["context_size"]}",
                "--keep -1",
                f"--model \"{text_model_path}\"",
                f"--mmproj \"{text_model_mmproj_path}\"" if text_model_mmproj_path != "" else "",
            ])
            match settings["server_init_settings"]["startup_behavior"]:
                case "separate_process":
                    os.startfile(os.path.abspath(llama_server_path), arguments=arguments)
                case "subprocess":
                    subprocess.Popen(f"{llama_server_path} {arguments}")
                case _:
                    error_and_exit("Invalid server startup behavior")
            break

    while True:
        try:
            if not is_llama_server_online:
                is_llama_server_online = opengpt_networking.get_llama_server_status(llama_server_url)
                if is_llama_server_online:
                    opengpt_utils.new_print("Server is online", opengpt_constants.PRINT_COLORS["success"])
            else:
                text_model_id, text_model_modalities = opengpt_networking.get_llama_server_info(llama_server_url)
                opengpt_utils.new_print(f"You are served by: {text_model_id}", opengpt_constants.PRINT_COLORS["success"])
                break
        except requests.exceptions.ConnectionError:
            error_and_exit("An error occurred while connecting to the server")

    opengpt_utils.new_print(f"\n{settings["mode"].capitalize()} Mode", opengpt_constants.PRINT_COLORS["special"])
    opengpt_utils.new_print("/help to see all commands.\n", opengpt_constants.PRINT_COLORS["special"])
    while True:
        match settings["mode"]:
            case "chat":
                user_message: str = input(opengpt_utils.colorize_text("USER: ", opengpt_constants.PRINT_COLORS["user_prefix"]))
                command: str = user_message.strip()

                if command.startswith(opengpt_constants.COMMAND_IMAGE_ALIAS):
                    pattern: str = opengpt_utils.build_params_regex_pattern(opengpt_constants.IMAGE_MODEL_GEN_PARAMS_SCHEMA, opengpt_constants.COMMAND_IMAGE_ALIAS, settings["image_model_settings"]["api_type"])

                    match: re.Match[str] | None = re.match(pattern, command)
                    if match is not None:
                        result, gen_time = opengpt_networking.generate_image(settings["image_model_settings"]["api_type"], image_gen_server_url, match)
                        if type(result) == dict:
                            # ensure that the image output directory exists.
                            try:
                                os.mkdir(opengpt_constants.IMAGE_MODEL_OUTPUT_DIR_NAME)
                            except FileExistsError:
                                pass

                            image_output_path: str = f"{opengpt_constants.IMAGE_MODEL_OUTPUT_DIR_NAME}{datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")}.png"
                            with open(image_output_path, "wb") as file:
                                file.write(base64.b64decode(result["image"].removeprefix("data:image/png;base64,")))
                            if settings["image_model_settings"]["open_output_on_gen"]:
                                os.startfile(os.path.abspath(image_output_path))

                            model_message: str = f"Generated in {"{:.2f}".format(gen_time)} seconds."
                            if not text_model_modalities.get("vision", False):
                                print(f"\n{opengpt_utils.colorize_text("MODEL: ", opengpt_constants.PRINT_COLORS["model_prefix"])}{model_message} This message won't be added to the context as I cannot see images.\n")
                        elif type(result) == str:
                            opengpt_utils.new_print(result, opengpt_constants.PRINT_COLORS["error"])
                elif command == opengpt_constants.COMMAND_HELP_ALIAS:
                    opengpt_utils.new_print("/image ", opengpt_constants.PRINT_COLORS["special"])
                elif command == opengpt_constants.COMMAND_EXIT_ALIAS:
                    exit()
                else:
                    command_attach_match: re.Match[str] | None = re.fullmatch(rf"(?P<command>(?:\s+)?{opengpt_constants.COMMAND_ATTACH_ALIAS}\s+\"(?P<path>[^\"]+)\")?", user_message)
                    if command_attach_match:
                        print(command_attach_match.groupdict())

                    if append_message("user", user_message):
                        payload: dict[str, Any] = {
                            "model": text_model_id,
                            "messages": text_model_chat_message_history,
                            "stream": settings["text_model_settings"]["response_stream"] in ["sse", "typewriter"],
                        }

                        opengpt_utils.new_print(f"\nMODEL: ", opengpt_constants.PRINT_COLORS["model_prefix"], "")
                        chat_response: requests.Response = requests.post(f"{llama_server_url}/v1/chat/completions", json=payload, stream=payload["stream"])
                        if not payload["stream"]:
                            chat_response_data: dict = chat_response.json()
                            if append_message("assistant", refine_message(chat_response_data["choices"][0]["message"]["content"], settings["text_model_settings"]["chat_include_thoughts_in_context"])):
                                print(refine_message(chat_response_data["choices"][0]["message"]["content"], settings["text_model_settings"]["chat_show_thoughts_in_nonstreamed_responses"]), end="")
                        else:
                            model_message_buffer: str = ""
                            for line in chat_response.iter_lines():
                                decoded_line: str = line.decode("utf-8")
                                if decoded_line.startswith("data: ") and not decoded_line.endswith("[DONE]"):
                                    content: str | None = json.loads(decoded_line[len("data: "):])["choices"][0]["delta"].get("content", "")
                                    if content is not None:
                                        model_message_buffer += content
                                        match settings["text_model_settings"]["response_stream"]:
                                            case "sse":
                                                print(content, end="", flush=True)
                                            case "typewriter":
                                                for character in content:
                                                    print(character, end="", flush=True)
                                                    time.sleep(0.05)
                            append_message("assistant", refine_message(model_message_buffer, settings["text_model_settings"]["chat_include_thoughts_in_context"]))
                        print("\n")
                    else:
                        opengpt_utils.new_print("Cannot send empty messages", opengpt_constants.PRINT_COLORS["error"])
            case "autocomplete":
                prompt: str = input(opengpt_utils.colorize_text("> ", opengpt_constants.PRINT_COLORS["user_prefix"]))
            case _:
                error_and_exit("")