from typing import Any
import os
import subprocess
import json
import base64
import re
import time
from datetime import datetime
import requests
import validators
import opengpt_constants
import opengpt_utils
import opengpt_internet

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
            "port": 8888,
            "response_stream": "sse",
            "chat_show_thoughts_in_nonstreamed_responses": True,
            "chat_include_thoughts_in_context": False,
            "autocomplete_max_tokens": 128,
        },
        "image_model_settings": {
            "port": 7801,
            "open_output_on_gen": False,
        },
    }
    text_model_server_url: str = "http://localhost:"
    is_text_model_server_active: bool = False
    text_model_id: str = ""
    text_model_modalities: dict[str, bool] = {
        "vision": False,
        "audio": False,
    }
    text_model_chat_message_history: list[dict[str, Any]] = []
    image_model_server_url: str = "http://localhost:"

    # noinspection PyShadowingNames
    def append_message(role: str, content: str, attachment_path: str="") -> bool:
        if role not in opengpt_constants.TEXT_MODEL_CHAT_ROLES:
            opengpt_utils.new_print(f"Cannot add messages from role '{role}' to the context", opengpt_constants.PRINT_COLORS["error"])
            return False

        attachment_name: str = os.path.basename(attachment_path)
        attachment_extension: str = opengpt_utils.get_file_extension(attachment_name)
        is_attachment_url: validators.ValidationError | bool = validators.url(attachment_path)

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

    opengpt_internet.check_for_updates()

    if os.path.exists(opengpt_constants.SETTINGS_PATH):
        try:
            with open(opengpt_constants.SETTINGS_PATH, "rt") as file:
                new_settings: dict = json.load(file)

                for key, value in settings.items():
                    if key in new_settings:
                        settings[key] = new_settings[key]
        except json.JSONDecodeError:
            opengpt_utils.new_print("Malformed settings file", opengpt_constants.PRINT_COLORS["warning"])
    with open(opengpt_constants.SETTINGS_PATH, "wt") as file:
        json.dump(settings, file, indent=4)

    text_model_server_url += str(settings["text_model_settings"]["port"])
    image_model_server_url += str(settings["image_model_settings"]["port"])

    try:
        is_text_model_server_active = opengpt_internet.get_server_status(settings["text_model_settings"]["port"])
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
            if not opengpt_utils.is_text_model_valid(text_model_path):
                opengpt_utils.new_print("File does not exist or is not a valid language model", opengpt_constants.PRINT_COLORS["error"])
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
            break

    while True:
        try:
            if not is_text_model_server_active:
                is_text_model_server_active = opengpt_internet.get_server_status(settings["text_model_settings"]["port"])
            else:
                text_model_server_model_info_response: requests.Response = requests.get(f"{text_model_server_url}/v1/models")
                text_model_server_properties_response: requests.Response = requests.get(f"{text_model_server_url}/props")
                text_model_server_properties_data: dict = text_model_server_properties_response.json()

                text_model_id = os.path.splitext(os.path.basename(text_model_server_model_info_response.json()["models"][0]["name"]))[0]
                for key, value in text_model_modalities.items():
                    if key in text_model_server_properties_data["modalities"] and text_model_server_properties_data["modalities"][key] == True:
                        text_model_modalities[key] = True
                opengpt_utils.new_print(f"Running {text_model_id} (Vision: {text_model_modalities["vision"]}, Audio: {text_model_modalities["audio"]})\n", opengpt_constants.PRINT_COLORS["success"])
                break
        except requests.exceptions.ConnectionError:
            opengpt_utils.new_print("An error occurred while connecting to the server", opengpt_constants.PRINT_COLORS["error"])
            time.sleep(3.0)
            exit()

    while True:
        match settings["mode"]:
            case "chat":
                user_message: str = input(opengpt_utils.colorize_text("USER: ", opengpt_constants.PRINT_COLORS["user_prefix"]))
                command: str = user_message.strip()

                if command.startswith(opengpt_constants.COMMAND_IMAGE_ALIAS):
                    try:
                        available_gen_params = opengpt_constants.IMAGE_MODEL_AVAILABLE_GEN_PARAMS.items()

                        pattern: str = rf"^{opengpt_constants.COMMAND_IMAGE_ALIAS}"
                        for gen_param_name, gen_param_info in available_gen_params:
                            gen_param_pattern: str = rf"\s+(?:{gen_param_name}=)?"
                            if gen_param_info["type"] == str:
                                gen_param_pattern += rf"\"(?P<{gen_param_info["maps_to"]}>[^\"]+)\""
                            elif gen_param_info["type"] == bool:
                                gen_param_pattern += rf"(?P<{gen_param_info["maps_to"]}>true|false)"
                            elif gen_param_info["type"] == float:
                                gen_param_pattern += rf"(?P<{gen_param_info["maps_to"]}>\d+\.\d+)"
                            elif gen_param_info["type"] == int:
                                gen_param_pattern += rf"(?P<{gen_param_info["maps_to"]}>\d+)"

                            if "default_value" in gen_param_info:
                                gen_param_pattern = rf"(?:{gen_param_pattern})?"

                            pattern += gen_param_pattern
                        pattern += r"$"

                        match: re.Match[str] | None = re.match(pattern, command)
                        if match:
                            headers: dict[str, str] = {
                                "Content-Type": "application/json",
                            }
                            image_model_session_response: requests.Response = requests.post(f"{image_model_server_url}/API/GetNewSession", json={}, headers=headers)
                            image_model_session_id: str = image_model_session_response.json()["session_id"]
                            image_model_list_response: requests.Response = requests.post(f"{image_model_server_url}/API/ListLoadedModels", json={"session_id": image_model_session_id}, headers=headers)
                            image_model_list: list = image_model_list_response.json()["models"]
                            image_model_id: str = ""

                            if len(image_model_list) == 0:
                                opengpt_utils.new_print("SwarmUI: No image models are loaded", opengpt_constants.PRINT_COLORS["error"])
                                continue
                            elif len(image_model_list) == 1:
                                image_model_id = image_model_list[0]["name"]
                            elif len(image_model_list) >= 2:
                                pass # TODO: provide the user with an option to select an image model if more than one is loaded

                            gen_params: dict[str, Any] = match.groupdict()
                            can_generate: bool = True
                            for gen_param_name, gen_param_info in available_gen_params:
                                real_name: str = gen_param_info["maps_to"]

                                if gen_params[real_name] is None and "default_value" in gen_param_info:
                                    gen_params[real_name] = gen_param_info["default_value"]

                                if type(gen_params[real_name]) == str:
                                    if gen_param_info["type"] == bool:
                                        match gen_params[real_name]:
                                            case "true":
                                                gen_params[real_name] = True
                                            case "false":
                                                gen_params[real_name] = False
                                            case _: # This should never happen.
                                                gen_params[real_name] = True if "default_value" not in gen_param_info else gen_param_info["default_value"]
                                    elif gen_param_info["type"] == float:
                                        gen_params[real_name] = float(gen_params[real_name])
                                    elif gen_param_info["type"] == int:
                                        gen_params[real_name] = int(gen_params[real_name])

                                if gen_param_info["type"] == str and "values" in gen_param_info and gen_params[real_name] not in gen_param_info["values"]:
                                    available_values: str = ""
                                    for index in range(len(gen_param_info["values"])):
                                        available_values += f"{gen_param_info["values"][index]}{", " if index != len(gen_param_info["values"]) - 1 else ""}"

                                    can_generate = False
                                    opengpt_utils.new_print(f"Invalid value passed to {gen_param_name} (values: {available_values})", opengpt_constants.PRINT_COLORS["error"])
                                    break
                                elif (gen_param_info["type"] == float or gen_param_info["type"] == int) and "min_value" in gen_param_info and "max_value" in gen_param_info and (gen_params[real_name] < gen_param_info["min_value"] or gen_params[real_name] > gen_param_info["max_value"]):
                                    can_generate = False
                                    opengpt_utils.new_print(f"Invalid value passed to {gen_param_name} (min. value: {gen_param_info["min_value"]}, max. value: {gen_param_info["max_value"]})", opengpt_constants.PRINT_COLORS["error"])
                                    break

                            if not can_generate:
                                continue

                            payload: dict[str, Any] = {
                                "session_id": image_model_session_id,
                                "model": image_model_id,
                                "images": 1,
                                "donotsave": True,
                                "seed": -1,
                            }
                            for key, value in gen_params.items():
                                payload[key] = value
                            image_model_gen_start_time: float = time.time()
                            opengpt_utils.new_print("Generating...", opengpt_constants.PRINT_COLORS["success"])
                            image_model_gen_response: requests.Response = requests.post(f"{image_model_server_url}/API/GenerateText2Image", json=payload, headers=headers)
                            image_model_gen_data: str = image_model_gen_response.json()["images"][0]

                            # Ensure that the image output directory exists.
                            try:
                                os.mkdir(opengpt_constants.IMAGE_MODEL_OUTPUT_DIR_NAME)
                            except FileExistsError:
                                pass

                            image_output_path: str = f"{opengpt_constants.IMAGE_MODEL_OUTPUT_DIR_NAME}{datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")}.png"
                            with open(image_output_path, "wb") as file:
                                file.write(base64.b64decode(image_model_gen_data.removeprefix("data:image/png;base64,")))
                            if settings["image_model_settings"]["open_output_on_gen"]:
                                os.startfile(os.path.abspath(image_output_path))

                            model_message: str = f"Generated in {"{:.2f}".format(time.time() - image_model_gen_start_time)} seconds."
                            if not text_model_modalities["vision"]:
                                print(f"\n{opengpt_utils.colorize_text("MODEL: ", opengpt_constants.PRINT_COLORS["model_prefix"])}{model_message} This message won't be added to the context as I cannot see images.\n")
                            else: # TODO: work on this after message sending is fully implemented
                                pass
                        else:
                            opengpt_utils.new_print("Usage: /image posprompt=\"woman, high quality, 4k\" negprompt=\"bad quality\" width=512 height=512 steps=20 cfgscale=5.0", opengpt_constants.PRINT_COLORS["special"])
                    except requests.exceptions.ConnectionError:
                        opengpt_utils.new_print("SwarmUI: Not running", opengpt_constants.PRINT_COLORS["error"])
                elif command == opengpt_constants.COMMAND_HELP_ALIAS:
                    pass
                elif command == opengpt_constants.COMMAND_EXIT_ALIAS:
                    exit()
                else:
                    command_match: re.Match[str] | None = re.match(rf"^(?P<text>.+?)?(?P<command_start>(?:\s+)?/attach)(?P<command_end>\s+\"(?P<path>[^\"]+)\")?$", user_message)
                    if command_match:
                        pass

                    if append_message("user", user_message):
                        payload: dict[str, Any] = {
                            "model": text_model_id,
                            "messages": text_model_chat_message_history,
                            "stream": settings["text_model_settings"]["response_stream"] in ["sse", "typewriter"],
                        }

                        opengpt_utils.new_print(f"\nMODEL: ", opengpt_constants.PRINT_COLORS["model_prefix"], "")
                        chat_response: requests.Response = requests.post(f"{text_model_server_url}/v1/chat/completions", json=payload, stream=payload["stream"])
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
                prompt: str = input(f"{opengpt_constants.PRINT_COLORS["user_prefix"]}> {opengpt_constants.PRINT_COLORS["reset"]}")