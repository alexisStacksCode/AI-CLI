import os
import subprocess
import base64
import json
import re
import colorama
import time
import datetime
import requests
import validators

if __name__ == "__main__":
    SCRIPT_SETTINGS_PATH: str = "settings.json"
    SCRIPT_MODES: list[str] = [
        "chat",
        "autocomplete",
    ]
    PRINT_COLORS: dict[str, str] = {
        "success": colorama.Fore.LIGHTGREEN_EX,
        "warning": colorama.Fore.LIGHTYELLOW_EX,
        "error": colorama.Fore.LIGHTRED_EX,
        "user_prefix": colorama.Fore.LIGHTBLUE_EX,
        "model_prefix": colorama.Fore.LIGHTMAGENTA_EX,
        "special": colorama.Fore.LIGHTCYAN_EX,
    }
    SERVER_CHECK_INTERVAL: float = 1.0
    SERVER_STARTUP_BEHAVIOR_OPTIONS: list[str] = [
        "separate_process",
        "subprocess",
    ]
    TEXT_MODEL_SERVER_FILENAME: str = "llama-server.exe"
    TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH: str = "chat_system_prompt.txt"
    TEXT_MODEL_CHAT_ROLES: list[str] = [
        "system",
        "user",
        "assistant",
    ]
    TEXT_MODEL_CACHE_TYPES: list[str] = [
        "f32",
        "f16",
        "bf16",
        "q8_0",
        "q4_0",
        "q4_1",
        "iq4_nl",
        "q5_0",
        "q5_1",
    ]
    TEXT_MODEL_EXTENSION: str = ".gguf"
    TEXT_MODEL_ATTACHMENT_GENERIC_URL_PATTERNS: list[str] = [
        r"https://github\.com/[^/]+/[^/]+/raw/",
        r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/",
        r"https://gitlab\.com/[^/]+/[^/]+/-/raw/",
        r"https://bitbucket\.org/[^/]+/[^/]+/raw/",
        r"https://huggingface\.co/[^/]+/[^/]+/raw/",
        r"https://pastebin\.com/raw/",
    ]
    TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES: list[str] = [
        "LICENSE",
        "CODEOWNERS",
        ".shellcheckrc",
        ".editorconfig",
        ".vscodeignore",
        ".pylintrc",
        ".npmrc",
        ".npmignore",
        ".nvmrc",
        ".eslintignore",
        ".prettierrc",
        ".prettierignore",
        ".eleventyignore",
        ".nuxtignore",
        "CNAME",
        "project.godot",
        "Makefile",
        "SConstruct",
        "SCsub",
        ".clang-format",
        ".clang-tidy",
        ".clangd",
        "Dockerfile",
        ".dockerignore",
        "Gemfile",
        ".gitattributes",
        ".gitignore",
        ".gitmodules",
    ]
    TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS: list[str] = [
        # Godot
        ".tscn",
        ".tres",
        ".gd", # GDScript
        ".shader",
        ".gdshader",
        ".gdextension",

        # Text File
        ".text",
        ".txt",

        # Markdown
        ".md",
        ".markdown",

        # reStructuredText
        ".rst",

        # Scalable Vector Graphics
        ".svg",

        # Comma-Separated Values
        ".csv",

        # Tab-Separated Values
        ".tsv",

        # JavaScript Object Notation
        ".json",
        ".jsonc",

        # Tom's Obvious, Minimal Language
        ".toml",

        # Extensible Markup Language
        ".xml",

        # YAML Ain't Markup Language
        ".yaml",
        ".yml",

        # Configuration File
        ".cnf",
        ".conf",
        ".cfg",
        ".cf",
        ".ini",

        # Shell Script
        ".sh",

        # Batch File
        ".bat",
        ".cmd",
        ".btm",

        # PowerShell
        ".ps1",
        ".psd1",
        ".psm1",
        ".ps1xml",
        ".psc1",
        ".pssc",
        ".psrc",

        # Assembly
        ".asm",
        ".s",
        ".inc",
        ".wla",
        ".src", # Lowercase due to how get_path_extension() works.

        # Fortran
        ".f90",
        ".f",
        ".for",

        # Pascal
        ".p",
        ".pp",
        ".pas",

        # Haskell
        ".hs",
        ".lhs",

        # Julia
        ".jl",

        # C (also identifiable as C++)
        ".c",
        ".h", # Also identifiable as Objective-C.

        # C++
        ".cc",
        ".cpp",
        ".cxx",
        ".c++",
        ".hh",
        ".hpp",
        ".hxx",
        ".h++",
        ".cppm",
        ".ixx",

        # C#
        ".cs",
        ".csx",

        # Objective-C & Objective-C++
        ".m",
        ".mm",

        # Rust
        ".rs",

        # D
        ".d",
        ".dd",
        ".di",

        # Python
        ".py",
        ".pyw",
        ".pyi",

        # Lua & Luau
        ".lua",
        ".luau",

        # Ruby
        ".rb",
        ".ru",

        # Go
        ".go",

        # Java
        ".java",
        ".properties",

        # Swift
        ".swift",

        # HTML5
        ".html",
        ".htm",

        # CSS & Sass & Sassy CSS & Stylus & Less
        ".css",
        ".sass",
        ".scss",
        ".styl",
        ".less",

        # PHP
        ".php",
        ".phtml",
        ".pht",
        ".phps",

        # ActionScript
        ".as",

        # Haxe
        ".hx",
        ".hxml",

        # JavaScript & JS++
        ".js",
        ".mjs",
        ".cjs",
        ".jspp",
        ".js++",
        ".jpp",
        ".jsx",

        # TypeScript & Ark TypeScript
        ".ts", # Also identifiable as ArkTS.
        ".tsx",
        ".mts",
        ".cts",
        ".ets",

        # Jupyter Notebook
        ".ipynb",

        # CoffeeScript
        ".coffee",

        # Dart
        ".dart",

        # Structured Query Language
        ".sql",

        # OpenGL Shading Language
        ".glsl",
        ".vert",
        ".tesc",
        ".tese",
        ".geom",
        ".frag",
        ".comp",

        # High-Level Shader Language
        ".hlsl",
    ]
    TEXT_MODEL_ATTACHMENT_IMAGE_EXTENSIONS: list[str] = [
        ".jpg",
        ".jpeg",
        ".jpe",
        ".jif",
        ".jfif",
        ".jfi",
        ".jxl",
        ".jls",
        ".jxr",
        ".hdp",
        ".wdp",
        ".png",
        ".tiff",
        ".tif",
        ".webp",
    ]
    TEXT_MODEL_ATTACHMENT_AUDIO_EXTENSIONS: list[str] = [
        ".wav",
        ".mp3",
    ]
    IMAGE_MODEL_SERVER_FILENAME: str = "koboldcpp.exe"
    IMAGE_MODEL_OUTPUT_DIR_NAME: str = "image_outputs/"
    IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS: list[str] = [
        "none",
        "cuda",
        "clblast",
        "vulkan",
    ]
    IMAGE_MODEL_EXTENSIONS: list[str] = [
        ".safetensors",
        ".gguf",
    ]
    IMAGE_MODEL_MAX_SERVER_CHECKS: int = 20
    COMMAND_IMAGE_ALIAS: str = "/image"
    COMMAND_ATTACH_ALIAS: str = "/attach"
    COMMAND_HELP_ALIAS: str = "/help"
    COMMAND_EXIT_ALIAS: str = "/exit"

    script_settings: dict = {
        "script_mode": "chat",
        "server_startup_behavior": "subprocess",
        "text_model_init_settings": {
            "server_port": 7820,
            "priority": 0,
            "use_flash_attention": True,
            "gpu_layers": 99,
            "use_gpu_for_mmproj": True,
            "use_continuous_batching": True,
            "logical_max_batch_size": 2048,
            "physical_max_batch_size": 2048,
            "cache_type_k": "f16",
            "cache_type_v": "f16",
            "cache_defragmentation_threshold": 0.1,
            "cache_reuse_size": 256,
            "use_context_shift": True,
            "context_size": 8192,
            "disable_mmproj": False,
        },
        "disable_url_attachments": False,
        "text_model_gen_settings": {
            "stream_responses": True,
            "temperature": 0.8,
            "top_k": 40,
            "top_p": 0.95,
            "min_p": 0.05,
            "typical_p": 1.0,
            "repetition_penalty": 1.1,
            "repetition_penalty_range": 64,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "dry_base": 1.75,
            "dry_multiplier": 0.0,
            "dry_allowed_length": 2,
            "xtc_probability": 0.0,
            "xtc_threshold": 0.1,
            "chat_show_thoughts_in_nonstreaming_mode": True,
            "chat_include_thoughts_in_history": False,
            "autocomplete_max_tokens": 128,
        },
        "enable_image_model_server_in_chat": False,
        "image_model_init_settings": {
            "server_port": 7821,
            "hardware_acceleration": "cuda",
            "quantize_safetensors_on_server_start": False,
            "use_vae_tiling": True,
        },
        "image_model_gen_settings": {
            "cfg_scale": 5,
            "steps": 20,
            "width": 512,
            "height": 512,
            "seed": -1,
            "clip_skip": -1,
            "sampler_name": "Euler a",
        },
        "open_image_output_on_gen": False,
    }
    text_model_server_url: str = "http://localhost:"
    text_model_server_active: bool = False
    text_model_id: str = ""
    text_model_modalities: dict[str, bool] = {
        "vision": False,
        "audio": False,
    }
    text_model_message_history: list[dict] = []
    image_model_server_url: str = "http://localhost:"
    image_model_server_active: bool = False

    def new_print(string: str, string_color: str, end: str="\n") -> None:
        print(f"{string_color}{string}{colorama.Style.RESET_ALL}", end=end)

    def append_message(role: str, message: str, _file_path: str="") -> bool:
        if role not in TEXT_MODEL_CHAT_ROLES:
            new_print(f"Cannot add messages from role '{role}' to the context", PRINT_COLORS["error"])
            return False

        is_message_empty: bool = message.rstrip() == ""
        file_path_length: int = len(_file_path)
        filename: str = os.path.basename(_file_path)
        file_extension: str = get_path_extension(_file_path, False)
        does_file_exist: bool = os.path.exists(_file_path)
        is_file_valid_url: bool = validators.url(_file_path)
        is_file_generic_url: bool = is_generic_url(_file_path)

        if script_settings["disable_url_attachments"] and role == TEXT_MODEL_CHAT_ROLES[1] and is_file_valid_url:
            new_print("URL attachments are disabled", PRINT_COLORS["warning"])
            return append_message(role, message)

        if (is_file_valid_url and is_file_generic_url) or filename in TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES or file_extension in TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS:
            if not is_file_generic_url:
                if not does_file_exist:
                    new_print("File not found", PRINT_COLORS["warning"])
                    return append_message(role, message)

                try:
                    with open(_file_path, "rt") as _file:
                        text_model_message_history.append({
                            "role": role,
                            "content": f"`{filename}`:\n\n```\n{_file.read()}\n```{f"\n\n{message}" if not is_message_empty else ""}",
                        })
                except UnicodeDecodeError:
                    new_print("File is unreadable", PRINT_COLORS["warning"])
                    return append_message(role, message)
            else:
                try:
                    url_content_response: requests.Response = requests.get(_file_path)
                    url_content_response.raise_for_status()
                    text_model_message_history.append({
                        "role": role,
                        "content": f"`{_file_path}`:\n\n```\n{url_content_response.text}\n```{f"\n\n{message}" if not is_message_empty else ""}",
                    })
                except requests.HTTPError:
                    new_print("URL not found", PRINT_COLORS["warning"])
                    return append_message(role, message)
                except requests.ConnectionError:
                    new_print("Failed to resolve URL", PRINT_COLORS["warning"])
                    return append_message(role, message)
            return True
        elif file_extension in TEXT_MODEL_ATTACHMENT_IMAGE_EXTENSIONS:
            if not is_file_valid_url and not does_file_exist:
                new_print("File not found", PRINT_COLORS["warning"])
                return append_message(role, message)

            if not text_model_modalities["vision"]:
                new_print(f"Vision is not enabled for '{text_model_id}'", PRINT_COLORS["warning"])
                return append_message(role, message)

            text_model_message_history.append({
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": get_image_data(_file_path) if not is_file_valid_url else _file_path,
                        },
                    },
                ]
            })
            return True
        elif file_extension in TEXT_MODEL_ATTACHMENT_AUDIO_EXTENSIONS:
            if not does_file_exist:
                new_print("File not found", PRINT_COLORS["warning"])
                return append_message(role, message)

            if not text_model_modalities["audio"]:
                new_print(f"Audio is not enabled for '{text_model_id}'", PRINT_COLORS["warning"])
                return append_message(role, message)

            text_model_message_history.append({
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "input_audio",
                        "input_audio": get_audio_data(_file_path),
                    },
                ]
            })
            return True

        if role == TEXT_MODEL_CHAT_ROLES[1] and is_message_empty and file_path_length == 0:
            return False

        if file_path_length > 0:
            new_print("File does not exist or is unsupported", PRINT_COLORS["warning"])
            if is_message_empty:
                return False
        text_model_message_history.append({
            "role": role,
            "content": message,
        })
        return True

    def get_current_script_mode() -> str:
        for script_mode in SCRIPT_MODES:
            if script_mode == script_settings["script_mode"]:
                return script_mode.capitalize()
        return "Unknown"

    def poll_text_model_server_api() -> None:
        text_model_health_response: requests.Response = requests.get(f"{text_model_server_url}/health")
        if text_model_health_response.status_code == 200:
            global text_model_server_active
            text_model_server_active = True
            new_print("Text model server is online", PRINT_COLORS["success"])

    def is_image_model_server_online() -> bool:
        try:
            image_model_info_response: requests.Response = requests.get(f"{image_model_server_url}/sdapi/v1/sd-models")
            if len(image_model_info_response.json()) > 0:
                new_print("Image model server is online\n", PRINT_COLORS["success"])
                return True
            return False
        except requests.exceptions.ConnectionError:
            return False

    def is_text_model_multimodal() -> bool:
        for _value in text_model_modalities.values():
            if _value:
                return True
        return False

    def construct_text_model_gen_parameters() -> dict:
        return {
            "temperature": script_settings["text_model_gen_settings"]["temperature"],
            "top_k": script_settings["text_model_gen_settings"]["top_k"],
            "top_p": script_settings["text_model_gen_settings"]["top_p"],
            "min_p": script_settings["text_model_gen_settings"]["min_p"],
            "typical_p": script_settings["text_model_gen_settings"]["typical_p"],
            "repeat_penalty": script_settings["text_model_gen_settings"]["repetition_penalty"],
            "repeat_last_n": script_settings["text_model_gen_settings"]["repetition_penalty_range"],
            "presence_penalty": script_settings["text_model_gen_settings"]["presence_penalty"],
            "frequency_penalty": script_settings["text_model_gen_settings"]["frequency_penalty"],
            "dry_base": script_settings["text_model_gen_settings"]["dry_base"],
            "dry_multiplier": script_settings["text_model_gen_settings"]["dry_multiplier"],
            "dry_allowed_length": script_settings["text_model_gen_settings"]["dry_allowed_length"],
            "xtc_probability": script_settings["text_model_gen_settings"]["xtc_probability"],
            "xtc_threshold": script_settings["text_model_gen_settings"]["xtc_threshold"],
        }

    def process_text(text: str, return_with_thoughts: bool) -> str:
        if return_with_thoughts or ("<think>" not in text and "</think>" not in text):
            return text

        text_buffer: str = ""
        for pattern_match in re.findall(r"(<think>.*?</think>\n*)(.*?)(?=<think>|$)", text, re.DOTALL):
            text_buffer += pattern_match[1]
        return text_buffer

    def strip_leading_and_trailing_quotes(text: str) -> str:
        return text.removeprefix("\"").removesuffix("\"")

    def get_path_extension(path: str, omit_dot: bool) -> str:
        path_extension: str = os.path.splitext(path)[1].lower()
        return path_extension if not omit_dot else path_extension[1:]

    def is_generic_url(url: str) -> bool:
        for url_pattern in TEXT_MODEL_ATTACHMENT_GENERIC_URL_PATTERNS:
            if re.search(url_pattern, url):
                return True
        return False

    def get_image_data(path: str) -> str:
        with open(path, "rb") as _file:
            return f"data:image/{get_path_extension(path, True)};base64,{base64.b64encode(_file.read()).decode()}"

    def get_audio_data(path: str) -> dict:
        with open(path, "rb") as _file:
            return {
                "data": base64.b64encode(_file.read()).decode(),
                "format": get_path_extension(path, True)
            }

    def construct_arguments(_arguments: list[str]) -> str:
        argument_buffer: str = ""
        for argument in _arguments:
            argument = argument.strip()
            if argument != "":
                argument_buffer += f"{argument} "
        return argument_buffer.rstrip()

    def clamp_float(_value: float, min_value: float, max_value: float) -> float:
        if _value < min_value:
            return min_value
        elif _value > max_value:
            return max_value
        return _value

    def clamp_int(_value: int, min_value: int, max_value: int) -> int:
        if _value < min_value:
            return min_value
        elif _value > max_value:
            return max_value
        return _value

    if os.path.exists(SCRIPT_SETTINGS_PATH):
        with open(SCRIPT_SETTINGS_PATH, "rt") as file:
            new_script_settings: dict = json.load(file)
            for key, value in script_settings.items():
                value_type = type(value)
                if key in new_script_settings and type(new_script_settings[key]) == value_type:
                    if value_type != dict:
                        script_settings[key] = new_script_settings[key]
                    else:
                        for subkey, subvalue in value.items():
                            if subkey in new_script_settings[key] and type(new_script_settings[key][subkey]) == type(subvalue):
                                script_settings[key][subkey] = new_script_settings[key][subkey]
                            else:
                                new_print(f"Malformed setting '{key}.{subkey}'", PRINT_COLORS["warning"])
                else:
                    new_print(f"Malformed setting '{key}'", PRINT_COLORS["warning"])

            # Validate script_mode.
            if script_settings["script_mode"] not in SCRIPT_MODES:
                script_settings["script_mode"] = SCRIPT_MODES[0]

            # Validate server_startup_behavior.
            if script_settings["server_startup_behavior"] not in SERVER_STARTUP_BEHAVIOR_OPTIONS:
                script_settings["server_startup_behavior"] = SERVER_STARTUP_BEHAVIOR_OPTIONS[1]

            # Validate text_model_init_settings.
            script_settings["text_model_init_settings"]["server_port"] = clamp_int(script_settings["text_model_init_settings"]["server_port"], 1000, 9999)
            script_settings["text_model_init_settings"]["priority"] = clamp_int(script_settings["text_model_init_settings"]["priority"], 0, 3)
            script_settings["text_model_init_settings"]["gpu_layers"] = max(script_settings["text_model_init_settings"]["gpu_layers"], 0)
            script_settings["text_model_init_settings"]["logical_max_batch_size"] = max(script_settings["text_model_init_settings"]["logical_max_batch_size"], 16)
            script_settings["text_model_init_settings"]["physical_max_batch_size"] = max(script_settings["text_model_init_settings"]["physical_max_batch_size"], 4)
            if script_settings["text_model_init_settings"]["cache_type_k"] not in TEXT_MODEL_CACHE_TYPES:
                script_settings["text_model_init_settings"]["cache_type_k"] = TEXT_MODEL_CACHE_TYPES[1]
            if script_settings["text_model_init_settings"]["cache_type_v"] not in TEXT_MODEL_CACHE_TYPES:
                script_settings["text_model_init_settings"]["cache_type_v"] = TEXT_MODEL_CACHE_TYPES[1]
            script_settings["text_model_init_settings"]["cache_reuse_size"] = max(script_settings["text_model_init_settings"]["cache_reuse_size"], 0)
            script_settings["text_model_init_settings"]["context_size"] = max(script_settings["text_model_init_settings"]["context_size"], 256)

            # Validate text_model_gen_settings.
            script_settings["text_model_gen_settings"]["temperature"] = clamp_float(script_settings["text_model_gen_settings"]["temperature"], 0.0, 2.0)
            script_settings["text_model_gen_settings"]["top_k"] = clamp_int(script_settings["text_model_gen_settings"]["top_k"], 0, 100)
            script_settings["text_model_gen_settings"]["top_p"] = clamp_float(script_settings["text_model_gen_settings"]["top_p"], 0.0, 1.0)
            script_settings["text_model_gen_settings"]["min_p"] = clamp_float(script_settings["text_model_gen_settings"]["min_p"], 0.0, 1.0)
            script_settings["text_model_gen_settings"]["typical_p"] = clamp_float(script_settings["text_model_gen_settings"]["typical_p"], 0.0, 1.0)
            script_settings["text_model_gen_settings"]["repetition_penalty"] = clamp_float(script_settings["text_model_gen_settings"]["repetition_penalty"], 1.0, 2.0)
            script_settings["text_model_gen_settings"]["repetition_penalty_range"] = clamp_int(script_settings["text_model_gen_settings"]["repetition_penalty_range"], -1, 8192)
            script_settings["text_model_gen_settings"]["presence_penalty"] = clamp_float(script_settings["text_model_gen_settings"]["presence_penalty"], -2.0, 2.0)
            script_settings["text_model_gen_settings"]["frequency_penalty"] = clamp_float(script_settings["text_model_gen_settings"]["frequency_penalty"], -2.0, 2.0)
            script_settings["text_model_gen_settings"]["dry_base"] = clamp_float(script_settings["text_model_gen_settings"]["dry_base"], 0.0, 8.0)
            script_settings["text_model_gen_settings"]["dry_multiplier"] = clamp_float(script_settings["text_model_gen_settings"]["dry_multiplier"], 0.0, 100.0)
            script_settings["text_model_gen_settings"]["dry_allowed_length"] = clamp_int(script_settings["text_model_gen_settings"]["dry_allowed_length"], 0, 100)
            script_settings["text_model_gen_settings"]["xtc_probability"] = clamp_float(script_settings["text_model_gen_settings"]["xtc_probability"], 0.0, 1.0)
            script_settings["text_model_gen_settings"]["xtc_threshold"] = clamp_float(script_settings["text_model_gen_settings"]["xtc_threshold"], 0.0, 1.0)
            script_settings["text_model_gen_settings"]["autocomplete_max_tokens"] = clamp_int(script_settings["text_model_gen_settings"]["autocomplete_max_tokens"], 16, 1024)

            # Validate image_model_init_settings.
            script_settings["image_model_init_settings"]["server_port"] = clamp_int(script_settings["image_model_init_settings"]["server_port"], 1000, 9999)
            if script_settings["image_model_init_settings"]["hardware_acceleration"] not in IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS:
                script_settings["image_model_init_settings"]["hardware_acceleration"] = IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[1]

            # TODO: Implement image_model_gen_settings validation.

            # Validate server ports.
            if script_settings["text_model_init_settings"]["server_port"] == script_settings["image_model_init_settings"]["server_port"]:
                script_settings["text_model_init_settings"]["server_port"] = 7820
            if script_settings["image_model_init_settings"]["server_port"] == script_settings["text_model_init_settings"]["server_port"]:
                script_settings["image_model_init_settings"]["server_port"] = 7821
    with open(SCRIPT_SETTINGS_PATH, "wt") as file:
        json.dump(script_settings, file, indent=4)

    # Initialize server URL variables.
    text_model_server_url += str(script_settings["text_model_init_settings"]["server_port"])
    image_model_server_url += str(script_settings["image_model_init_settings"]["server_port"])

    # If the system prompt is specified and the script is running in Chat Mode, add it to the context.
    if script_settings["script_mode"] == SCRIPT_MODES[0] and os.path.exists(TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH):
        try:
            with open(TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH, "rt") as file:
                file_contents: str = file.read().strip()
                if file_contents != "":
                    append_message(TEXT_MODEL_CHAT_ROLES[0], file_contents)
        except UnicodeDecodeError:
            new_print("Malformed system prompt", PRINT_COLORS["warning"])

    new_print(f"Script will run in {get_current_script_mode()} Mode\n", PRINT_COLORS["special"])

    try:
        poll_text_model_server_api()
    except requests.exceptions.ConnectionError:
        while True:
            llama_cpp_dir_path: str = strip_leading_and_trailing_quotes(input("Enter the path to llama.cpp: "))
            llama_server_path: str = f"{llama_cpp_dir_path}{TEXT_MODEL_SERVER_FILENAME}"
            if os.path.exists(llama_server_path):
                break
            new_print(f"Directory is invalid or does not contain {TEXT_MODEL_SERVER_FILENAME}", PRINT_COLORS["error"])

        while True:
            text_model_path: str = strip_leading_and_trailing_quotes(input("Enter a text model path: "))
            if os.path.exists(text_model_path) and get_path_extension(text_model_path, False) == TEXT_MODEL_EXTENSION:
                break
            new_print("File does not exist or is not a text model", PRINT_COLORS["error"])

        new_print("Starting llama.cpp (text model server)", PRINT_COLORS["success"])
        text_model_mmproj_path: str = f"{text_model_path.removesuffix(TEXT_MODEL_EXTENSION)}-mmproj{TEXT_MODEL_EXTENSION}"
        does_text_model_mmproj_exist: bool = os.path.exists(text_model_mmproj_path) if not script_settings["text_model_init_settings"]["disable_mmproj"] else False
        arguments: str = construct_arguments([
            f"--port {script_settings["text_model_init_settings"]["server_port"]}",
            f"--prio-batch {script_settings["text_model_init_settings"]["priority"]}",
            "--flash-attn" if script_settings["text_model_init_settings"]["use_flash_attention"] else "",
            f"--gpu-layers {script_settings["text_model_init_settings"]["gpu_layers"]}",
            "--no-mmproj-offload" if does_text_model_mmproj_exist and not script_settings["text_model_init_settings"]["use_gpu_for_mmproj"] else "",
            "--cont-batching" if script_settings["text_model_init_settings"]["use_continuous_batching"] else "--no-cont-batching",
            f"--batch-size {script_settings["text_model_init_settings"]["logical_max_batch_size"]}",
            f"--ubatch-size {script_settings["text_model_init_settings"]["physical_max_batch_size"]}",
            f"--cache-type-k {script_settings["text_model_init_settings"]["cache_type_k"]}",
            f"--cache-type-v {script_settings["text_model_init_settings"]["cache_type_v"]}",
            f"--defrag-thold {script_settings["text_model_init_settings"]["cache_defragmentation_threshold"]}",
            f"--cache-reuse {script_settings["text_model_init_settings"]["cache_reuse_size"]}",
            "--no-context-shift" if not script_settings["text_model_init_settings"]["use_context_shift"] else "",
            f"--model \"{text_model_path}\"",
            f"--mmproj \"{text_model_mmproj_path}\"" if does_text_model_mmproj_exist else "",
            f"--ctx-size {script_settings["text_model_init_settings"]["context_size"]}",
            "--keep -1",
        ])
        if script_settings["server_startup_behavior"] == SERVER_STARTUP_BEHAVIOR_OPTIONS[0]:
            os.startfile(llama_server_path, arguments=arguments)
        elif script_settings["server_startup_behavior"] == SERVER_STARTUP_BEHAVIOR_OPTIONS[1]:
            subprocess.Popen(f"{llama_server_path} {arguments}", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    while True:
        if not text_model_server_active:
            try:
                poll_text_model_server_api()
            except requests.exceptions.ConnectionError:
                new_print("Text model server was closed", PRINT_COLORS["error"])
                exit()
        else:
            try:
                text_model_info_response: requests.Response = requests.get(f"{text_model_server_url}/v1/models")
                text_model_id = text_model_info_response.json()["data"][0]["id"]

                text_model_properties_response: requests.Response = requests.get(f"{text_model_server_url}/props")
                text_model_properties: dict = text_model_properties_response.json()
                for key, value in text_model_properties["modalities"].items():
                    if key in text_model_modalities:
                        text_model_modalities[key] = value
                    else:
                        new_print(f"Text model server supports modality '{key}' but it's not implemented in the script", PRINT_COLORS["warning"])

                text_model_modalities_string: str = ""
                for key, value in text_model_modalities.items():
                    text_model_modalities_string += f"{key.capitalize()}: {value}, "
                text_model_modalities_string = text_model_modalities_string.removesuffix(", ")
                new_print(f"Running {text_model_id}{f" ({text_model_modalities_string})" if len(text_model_modalities) > 0 else ""}\n", PRINT_COLORS["success"])
                break
            except requests.exceptions.ConnectionError:
                new_print("Text model server was closed", PRINT_COLORS["error"])
                exit()
        time.sleep(SERVER_CHECK_INTERVAL)

    # NOTE: KoboldCpp is used to allow the script to interface with stable-diffusion.cpp.
    if script_settings["script_mode"] == SCRIPT_MODES[0] and script_settings["enable_image_model_server_in_chat"]:
        image_model_server_active = is_image_model_server_online()
        if not image_model_server_active:
            while True:
                koboldcpp_dir_path: str = strip_leading_and_trailing_quotes(input("Enter the path to KoboldCpp: "))
                koboldcpp_path: str = f"{koboldcpp_dir_path}{IMAGE_MODEL_SERVER_FILENAME}"
                if os.path.exists(koboldcpp_path):
                    break
                new_print(f"Directory is invalid or does not contain {IMAGE_MODEL_SERVER_FILENAME}", PRINT_COLORS["error"])

            while True:
                image_model_path: str = strip_leading_and_trailing_quotes(input("Enter an image model path: "))
                image_model_extension: str = get_path_extension(image_model_path, False)
                if os.path.exists(image_model_path) and image_model_extension in IMAGE_MODEL_EXTENSIONS:
                    break
                new_print("File does not exist or is not an image model", PRINT_COLORS["error"])

            new_print("Starting KoboldCpp (image model server)", PRINT_COLORS["success"])
            arguments: str = construct_arguments([
                "--skiplauncher",
                f"--port {script_settings["image_model_init_settings"]["server_port"]}",
                "--usecpu" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[0] else "",
                "--usecublas" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[1] else "",
                "--useclblast 0 0" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[2] else "",
                "--usevulkan" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[3] else "",
                "--nomodel",
                f"--sdmodel \"{image_model_path}\"",
                "--sdnotile" if not script_settings["image_model_init_settings"]["use_vae_tiling"] else "",
                "--sdquant" if image_model_extension == IMAGE_MODEL_EXTENSIONS[0] and script_settings["image_model_init_settings"]["quantize_safetensors_on_server_start"] else "",
            ])
            if script_settings["server_startup_behavior"] == SERVER_STARTUP_BEHAVIOR_OPTIONS[0]:
                os.startfile(koboldcpp_path, arguments=arguments)
            elif script_settings["server_startup_behavior"] == SERVER_STARTUP_BEHAVIOR_OPTIONS[1]:
                subprocess.Popen(f"{koboldcpp_path} {arguments}", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            image_model_server_checks: int = 0
            while True:
                if image_model_server_checks > IMAGE_MODEL_MAX_SERVER_CHECKS:
                    new_print("Image model server was closed or image model took too long to load\n", PRINT_COLORS["error"])
                    break

                image_model_server_checks += 1
                image_model_server_active = is_image_model_server_online()
                if image_model_server_active:
                    break
                time.sleep(SERVER_CHECK_INTERVAL)

    while True:
        if script_settings["script_mode"] == SCRIPT_MODES[0]: # Chat Mode
            user_message: str = input(f"{PRINT_COLORS["user_prefix"]}USER: {colorama.Style.RESET_ALL}")
            command: str = user_message.strip()

            if command == COMMAND_IMAGE_ALIAS:
                if not image_model_server_active:
                    new_print("Image model server is offline", PRINT_COLORS["error"])
                    continue

                image_positive_prompt: str = input("Enter a positive prompt: ").strip()
                if image_positive_prompt == "":
                    new_print("Cannot generate images with an empty positive prompt", PRINT_COLORS["error"])
                    continue
                image_negative_prompt: str = input("Enter a negative prompt (optional): ").strip()
                new_print("Generating...", PRINT_COLORS["success"])

                try:
                    payload: dict = {
                        "prompt": image_positive_prompt,
                        "negative_prompt": image_negative_prompt,
                    }
                    for key, value in script_settings["image_model_gen_settings"].items():
                        payload[key] = value
                    image_generation_start_time: float = time.time()
                    image_response: requests.Response = requests.post(f"{image_model_server_url}/sdapi/v1/txt2img", json=payload)

                    # Ensure that the image output directory exists.
                    try:
                        os.mkdir(IMAGE_MODEL_OUTPUT_DIR_NAME)
                    except FileExistsError:
                        pass

                    image_output_path: str = f"{IMAGE_MODEL_OUTPUT_DIR_NAME}{datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")}.png"
                    with open(image_output_path, "wb") as file:
                        file.write(base64.b64decode(image_response.json()["images"][0]))
                    if script_settings["open_image_output_on_gen"]:
                        os.startfile(os.path.abspath(image_output_path))
                    model_message: str = f"Generated in {"{:.2f}".format(time.time() - image_generation_start_time)} seconds."
                    if text_model_modalities["vision"]:
                        if image_negative_prompt == "":
                            append_message(TEXT_MODEL_CHAT_ROLES[1], f"**Prompt:** {image_positive_prompt}\n\nGenerate an image using the provided prompt.")
                        else:
                            append_message(TEXT_MODEL_CHAT_ROLES[1], f"**Positive Prompt:** {image_positive_prompt}\n**Negative Prompt:** {image_negative_prompt}\n\nGenerate an image using the provided positive prompt and negative prompt.")
                        if append_message(TEXT_MODEL_CHAT_ROLES[2], model_message, image_output_path):
                            print(f"\n{PRINT_COLORS["model_prefix"]}MODEL: {colorama.Style.RESET_ALL}{model_message}\n")
                    else:
                        print(f"\n{PRINT_COLORS["model_prefix"]}MODEL: {colorama.Style.RESET_ALL}{model_message} This message won't be added to the context as I cannot see images.\n")
                except requests.exceptions.ConnectionError:
                    image_model_server_active = False
                    new_print("Image model server was closed", PRINT_COLORS["error"])
            elif command == COMMAND_HELP_ALIAS:
                new_print(f"{COMMAND_IMAGE_ALIAS} - Generate an image (requires the image model server to be online).", PRINT_COLORS["special"])
                new_print(f"{COMMAND_ATTACH_ALIAS} - Attach a file or URL to your message (command must be at the end of your message).", PRINT_COLORS["special"])
                new_print(f"{COMMAND_HELP_ALIAS} - Display all commands.", PRINT_COLORS["special"])
                new_print(f"{COMMAND_EXIT_ALIAS} - Exit the application.", PRINT_COLORS["special"])
            elif command == COMMAND_EXIT_ALIAS:
                break
            else:
                file_path: str = ""

                if command.endswith(COMMAND_ATTACH_ALIAS):
                    file_path = strip_leading_and_trailing_quotes(input("Enter a file path or URL: "))
                    user_message = user_message.removesuffix(COMMAND_ATTACH_ALIAS).rstrip()

                if append_message(TEXT_MODEL_CHAT_ROLES[1], user_message, file_path):
                    try:
                        payload: dict = {
                            "model": text_model_id,
                            "messages": text_model_message_history,
                            "stream": script_settings["text_model_gen_settings"]["stream_responses"],
                        }
                        for key, value in construct_text_model_gen_parameters().items():
                            payload[key] = value

                        new_print("\nMODEL: ", PRINT_COLORS["model_prefix"], "")
                        chat_response: requests.Response = requests.post(f"{text_model_server_url}/v1/chat/completions", json=payload, stream=script_settings["text_model_gen_settings"]["stream_responses"])
                        if not script_settings["text_model_gen_settings"]["stream_responses"]:
                            chat_response_data: dict = chat_response.json()
                            if "error" not in chat_response_data:
                                model_message: str = chat_response_data["choices"][0]["message"]["content"]
                                if append_message(TEXT_MODEL_CHAT_ROLES[2], process_text(model_message, script_settings["text_model_gen_settings"]["chat_include_thoughts_in_history"])):
                                    print(f"{process_text(model_message, script_settings["text_model_gen_settings"]["chat_show_thoughts_in_nonstreaming_mode"])}\n")
                            else:
                                match chat_response_data["error"]["message"]:
                                    case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                        print("Your message exceeds the available context size. Try increasing the context size or enable Context Shift.", end="")
                                    case "Failed to load image or audio file":
                                        print("This file is not encodable.", end="")
                                    case _:
                                        print("An error occurred.", end="")
                                print(" This message won't be added to the context.\n")
                                text_model_message_history.pop()
                        else:
                            model_message_buffer: str = ""

                            # Streaming code based on: https://gist.github.com/ggorlen/7c944d73e27980544e29aa6de1f2ac54
                            for line in chat_response.iter_lines():
                                decoded_line: str = line.decode("utf-8")
                                if decoded_line.startswith("data: ") and not decoded_line.endswith("[DONE]"):
                                    chunk: str | None = json.loads(line[len("data: "):])["choices"][0]["delta"].get("content", "")
                                    if chunk is not None:
                                        model_message_buffer += chunk
                                        print(chunk, end="", flush=True)
                                elif decoded_line.startswith("error: "):
                                    match json.loads(line[len("error: "):])["message"]:
                                        case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                            new_print("Your message exceeds the available context size. Try increasing the context size or enable Context Shift.", PRINT_COLORS["error"], "")
                                        case _:
                                            new_print("An error occurred.", PRINT_COLORS["error"], "")
                                    print(" This message won't be added to the context.", end="")
                                    text_model_message_history.pop()
                                    break
                                elif decoded_line.startswith("{\"error\":"):
                                    match json.loads(decoded_line)["error"]["message"]:
                                        case "Failed to load image or audio file":
                                            new_print("This file is not encodable.", PRINT_COLORS["error"], "")
                                        case _:
                                            new_print("An error occurred.", PRINT_COLORS["error"], "")
                                    print(" This message won't be added to the context.", end="")
                                    text_model_message_history.pop()
                                    break
                            if model_message_buffer != "":
                                append_message(TEXT_MODEL_CHAT_ROLES[2], process_text(model_message_buffer, script_settings["text_model_gen_settings"]["chat_include_thoughts_in_history"]))
                            print("\n")
                    except requests.exceptions.ConnectionError:
                        new_print("Text model server was closed", PRINT_COLORS["error"])
                        break
                    except requests.exceptions.ChunkedEncodingError:
                        new_print("\nText model server was closed", PRINT_COLORS["error"])
                        break
                else:
                    new_print("Cannot send empty messages", PRINT_COLORS["error"])
        elif script_settings["script_mode"] == SCRIPT_MODES[1]: # Autocomplete Mode
            prompt: str = input(f"{PRINT_COLORS["user_prefix"]}> {colorama.Style.RESET_ALL}")
            try:
                payload: dict = {
                    "model": text_model_id,
                    "prompt": prompt,
                    "stream": script_settings["text_model_gen_settings"]["stream_responses"],
                    "n_predict": script_settings["text_model_gen_settings"]["autocomplete_max_tokens"],
                }
                for key, value in construct_text_model_gen_parameters().items():
                    payload[key] = value

                text_response: requests.Response = requests.post(f"{text_model_server_url}/completion", json=payload, stream=script_settings["text_model_gen_settings"]["stream_responses"])
                if not script_settings["text_model_gen_settings"]["stream_responses"]:
                    text_response_data: dict = text_response.json()
                    if "error" not in text_response_data:
                        new_print(f"{prompt}{text_response_data["content"]}\n", PRINT_COLORS["model_prefix"])
                    else:
                        match text_response_data["error"]["message"]:
                            case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                new_print("Your prompt exceeds the available context size. Try increasing the context size or enable Context Shift.\n", PRINT_COLORS["error"])
                            case _:
                                new_print("An error occurred.\n", PRINT_COLORS["error"])
                else:
                    was_prompt_printed: bool = False
                    for line in text_response.iter_lines():
                        decoded_line: str = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            if not was_prompt_printed:
                                was_prompt_printed = True
                                print(f"{PRINT_COLORS["model_prefix"]}{prompt}", end="")
                            print(json.loads(line[len("data: "):])["content"], end="", flush=True)
                        elif decoded_line.startswith("error: "):
                            match json.loads(line[len("error: "):])["message"]:
                                case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                    new_print("Your prompt exceeds the available context size. Try increasing the context size or enable Context Shift.", PRINT_COLORS["error"], "")
                                case _:
                                    new_print("An error occurred.", PRINT_COLORS["error"], "")
                            break
                    print("\n")
            except requests.exceptions.ConnectionError:
                print("Text model server was closed")
                break
            except requests.exceptions.ChunkedEncodingError:
                print("\nText model server was closed")
                break