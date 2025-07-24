import os
import base64
import json
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
    SERVER_CHECK_INTERVAL: float = 1.0
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
    IMAGE_MODEL_LORA_EXTENSION: str = ".safetensors"
    IMAGE_MODEL_MAX_SERVER_CHECKS: int = 20
    COMMAND_IMAGE_ALIAS: str = "/image"
    COMMAND_ATTACH_ALIAS: str = "/attach"
    COMMAND_HELP_ALIAS: str = "/help"
    COMMAND_EXIT_ALIAS: str = "/exit"

    script_settings: dict = {
        "script_mode": "chat", # Valid values: "chat", "autocomplete"
        "text_model_init_settings": {
            "server_port": 8080,
            "priority": 0,
            "use_flash_attention": True,
            "gpu_layers": 99,
            "use_gpu_for_mmproj": True,
            "use_continuous_batching": True,
            "logical_max_batch_size": 2048,
            "physical_max_batch_size": 512,
            "cache_type_k": "f16",
            "cache_type_v": "f16",
            "cache_defragmentation_threshold": 0.1,
            "cache_reuse_size": 0,
            "use_context_shift": True,
            "context_size": 8192,
            "disable_mmproj": False,
        },
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
            "chat_include_thoughts_in_history": False,
            "autocomplete_max_tokens": 128,
        },
        "enable_image_model_server_in_chat": False,
        "image_model_init_settings": {
            "server_port": 5001,
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

    def append_message(role: str, message: str, _file_path: str="") -> bool:
        if role not in TEXT_MODEL_CHAT_ROLES:
            print(f"Cannot add messages from role '{role}' to the context!")
            return False

        is_message_empty: bool = message.rstrip() == ""
        file_path_length: int = len(_file_path)
        file_extension: str = get_path_extension(_file_path, False)
        is_file_url: bool = validators.url(_file_path)
        does_file_exist: bool = os.path.exists(_file_path)

        if os.path.basename(_file_path) in TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES or file_extension in TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS:
            if not does_file_exist:
                print("File does not exist")
                return append_message(role, message)

            try:
                with open(_file_path, "rt") as _file:
                    text_model_message_history.append({
                        "role": role,
                        "content": f"`{os.path.basename(_file_path)}`:\n\n```\n{_file.read()}\n```{f"\n\n{message}" if not is_message_empty else ""}"
                    })
            except UnicodeDecodeError:
                print("File is unreadable")
                return append_message(role, message)
            return True
        elif file_extension in TEXT_MODEL_ATTACHMENT_IMAGE_EXTENSIONS:
            if not is_file_url and not does_file_exist:
                print("File does not exist")
                return append_message(role, message)

            if not text_model_modalities["vision"]:
                print(f"Vision is not enabled for '{text_model_id}'")
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
                            "url": _file_path if is_file_url else get_image_data(_file_path),
                        },
                    },
                ]
            })
            return True
        elif file_extension in TEXT_MODEL_ATTACHMENT_AUDIO_EXTENSIONS:
            if not does_file_exist:
                print("File does not exist")
                return append_message(role, message)

            if not text_model_modalities["audio"]:
                print(f"Audio is not enabled for '{text_model_id}'")
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
            print("File does not exist or is unsupported")
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
            print("Text model server is online")

    def is_image_model_server_online() -> bool:
        try:
            image_model_info_response: requests.Response = requests.get(f"{image_model_server_url}/sdapi/v1/sd-models")
            if len(image_model_info_response.json()) > 0:
                print("Image model server is online\n")
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

    def strip_thoughts(text: str) -> str:
        return text.split("</think>\n\n", 1)[1] if script_settings["text_model_gen_settings"]["chat_include_thoughts_in_history"] and "<think>" in text and "</think>" in text else text

    def strip_leading_and_trailing_quotes(text: str) -> str:
        return text.removeprefix("\"").removesuffix("\"")

    def get_path_extension(path: str, omit_dot: bool) -> str:
        path_extension: str = os.path.splitext(path)[1].lower()
        return path_extension if not omit_dot else path_extension[1:]

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
                                print(f"Malformed setting '{key}.{subkey}'")
                else:
                    print(f"Malformed setting '{key}'")

            # Validate script_mode.
            if script_settings["script_mode"] not in SCRIPT_MODES:
                script_settings["script_mode"] = SCRIPT_MODES[0]

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
            script_settings["text_model_gen_settings"]["autocomplete_max_tokens"] = max(script_settings["text_model_gen_settings"]["autocomplete_max_tokens"], 16)

            # Validate image_model_init_settings.
            script_settings["image_model_init_settings"]["server_port"] = clamp_int(script_settings["image_model_init_settings"]["server_port"], 1000, 9999)
            if script_settings["image_model_init_settings"]["hardware_acceleration"] not in IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS:
                script_settings["image_model_init_settings"]["hardware_acceleration"] = IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[1]

            # TODO: Implement image_model_gen_settings validation.

            # Validate server ports.
            if script_settings["text_model_init_settings"]["server_port"] == script_settings["image_model_init_settings"]["server_port"]:
                script_settings["text_model_init_settings"]["server_port"] = 8080
            if script_settings["image_model_init_settings"]["server_port"] == script_settings["text_model_init_settings"]["server_port"]:
                script_settings["image_model_init_settings"]["server_port"] = 5001
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
            print("Malformed system prompt")

    print(f"Script will run in {get_current_script_mode()} Mode\n")

    try:
        poll_text_model_server_api()
    except requests.exceptions.ConnectionError:
        llama_cpp_dir_path: str = strip_leading_and_trailing_quotes(input("Enter the path to llama.cpp: "))
        llama_server_path: str = f"{llama_cpp_dir_path}{TEXT_MODEL_SERVER_FILENAME}"
        if not os.path.exists(llama_server_path):
            print("Invalid path!")
            exit()

        text_model_path: str = strip_leading_and_trailing_quotes(input("Enter the path to your desired text model: "))
        if not os.path.exists(text_model_path) or get_path_extension(text_model_path, False) != TEXT_MODEL_EXTENSION:
            print("File does not exist or is not a valid model!")
            exit()

        print("Starting llama.cpp (text model server)")
        text_model_mmproj_path: str = f"{text_model_path.removesuffix(TEXT_MODEL_EXTENSION)}-mmproj{TEXT_MODEL_EXTENSION}"
        does_text_model_mmproj_exist: bool = os.path.exists(text_model_mmproj_path) if not script_settings["text_model_init_settings"]["disable_mmproj"] else False
        arguments: list[str] = [
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
        ]
        os.startfile(llama_server_path, arguments=construct_arguments(arguments))

    while True:
        if not text_model_server_active:
            try:
                poll_text_model_server_api()
            except requests.exceptions.ConnectionError:
                print("Text model server was closed")
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
                        print(f"Text model server supports modality '{key}' but it's not implemented in the script")

                text_model_modalities_string: str = ""
                for key, value in text_model_modalities.items():
                    text_model_modalities_string += f"{key.capitalize()}: {value}, "
                text_model_modalities_string = text_model_modalities_string.removesuffix(", ")
                print(f"Running {text_model_id}{f" ({text_model_modalities_string})" if len(text_model_modalities) > 0 else ""}\n")
                break
            except requests.exceptions.ConnectionError:
                print("Text model server was closed")
                exit()
        time.sleep(SERVER_CHECK_INTERVAL)

    # NOTE: KoboldCpp is used to allow the script to interface with stable-diffusion.cpp.
    if script_settings["script_mode"] == SCRIPT_MODES[0] and script_settings["enable_image_model_server_in_chat"]:
        image_model_server_active = is_image_model_server_online()
        if not image_model_server_active:
            koboldcpp_dir_path: str = strip_leading_and_trailing_quotes(input("Enter the path to KoboldCpp: "))
            koboldcpp_path: str = f"{koboldcpp_dir_path}koboldcpp.exe"
            if not os.path.exists(koboldcpp_path):
                print("Invalid path!")
                exit()

            image_model_path: str = strip_leading_and_trailing_quotes(input("Enter the path to your desired image model: "))
            image_model_extension: str = get_path_extension(image_model_path, False)
            if not os.path.exists(image_model_path) or image_model_extension not in IMAGE_MODEL_EXTENSIONS:
                print("File does not exist or is not a valid model!")
                exit()

            image_model_lora_path: str = ""
            image_model_lora_multiplier: float = 0.5
            if image_model_extension == IMAGE_MODEL_EXTENSIONS[0]:
                image_model_lora_path = strip_leading_and_trailing_quotes(input("Enter the path to the LoRA you want to apply to the image model (optional): "))
                if os.path.exists(image_model_lora_path) and get_path_extension(image_model_lora_path, False) == IMAGE_MODEL_LORA_EXTENSION:
                    try:
                        image_model_lora_multiplier = float(input("Enter the LoRA multiplier: "))
                        if image_model_lora_multiplier < 0.0:
                            image_model_lora_multiplier = 0.0
                            print("LoRA multiplier cannot be lower than 0.0")
                        elif image_model_lora_multiplier > 1.0:
                            image_model_lora_multiplier = 1.0
                            print("LoRA multiplier cannot be higher than 1.0")
                    except ValueError:
                        print(f"Invalid value, defaulting to {image_model_lora_multiplier}")
                else:
                    if len(image_model_lora_path) > 0:
                        print("File does not exist or is not a valid LoRA!")
                    image_model_lora_path = ""

            print("Starting KoboldCpp (image model server)")
            arguments: list[str] = [
                "--skiplauncher",
                f"--port {script_settings["image_model_init_settings"]["server_port"]}",
                "--usecpu" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[0] else "",
                "--usecublas" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[1] else "",
                "--useclblast 0 0" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[2] else "",
                "--usevulkan" if script_settings["image_model_init_settings"]["hardware_acceleration"] == IMAGE_MODEL_HARDWARE_ACCELERATION_OPTIONS[3] else "",
                "--nomodel",
                f"--sdmodel \"{image_model_path}\"",
                f"--sdlora \"{image_model_lora_path}\"" if image_model_lora_path != "" else "",
                f"--sdloramult {image_model_lora_multiplier}" if image_model_lora_path != "" else "",
                "--sdnotile" if not script_settings["image_model_init_settings"]["use_vae_tiling"] else "",
                "--sdquant" if image_model_extension == IMAGE_MODEL_EXTENSIONS[0] and script_settings["image_model_init_settings"]["quantize_safetensors_on_server_start"] else "",
            ]
            os.startfile(koboldcpp_path, arguments=construct_arguments(arguments))

            image_model_server_checks: int = 0
            while True:
                if image_model_server_checks > IMAGE_MODEL_MAX_SERVER_CHECKS:
                    print("Image model server was closed or image model took too long to load\n")
                    break

                image_model_server_checks += 1
                image_model_server_active = is_image_model_server_online()
                if image_model_server_active:
                    break
                time.sleep(SERVER_CHECK_INTERVAL)

    while True:
        if script_settings["script_mode"] == SCRIPT_MODES[0]: # Chat Mode
            user_message: str = input("USER: ")
            command: str = user_message.strip()

            if command == COMMAND_IMAGE_ALIAS:
                if not image_model_server_active:
                    print("Image model server is offline")
                    continue

                image_positive_prompt: str = input("Enter a positive prompt: ").strip()
                if image_positive_prompt == "":
                    print("Cannot generate images with an empty positive prompt!")
                    continue
                image_negative_prompt: str = input("Enter a negative prompt (optional): ").strip()
                print("Generating...")

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
                            print(f"\nMODEL: {model_message}\n")
                    else:
                        print(f"\nMODEL: {model_message} This message won't be added to the context as vision is not enabled for '{text_model_id}'.\n")
                except requests.exceptions.ConnectionError:
                    image_model_server_active = False
                    print("Image model server was closed")
            elif command == COMMAND_HELP_ALIAS:
                print(f"{COMMAND_IMAGE_ALIAS} - Generate an image (requires the image model server to be online).")
                print(f"{COMMAND_ATTACH_ALIAS} - Attach a file or image URL to your message (must be at the end of your message).")
                print(f"{COMMAND_HELP_ALIAS} - Show all commands.")
                print(f"{COMMAND_EXIT_ALIAS} - Exit the application.")
            elif command == COMMAND_EXIT_ALIAS:
                break
            else:
                file_path: str = ""

                if command.endswith(COMMAND_ATTACH_ALIAS):
                    file_path = strip_leading_and_trailing_quotes(input("Enter the path to the file that will be attached to your message: "))
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

                        chat_response: requests.Response = requests.post(f"{text_model_server_url}/v1/chat/completions", json=payload, stream=script_settings["text_model_gen_settings"]["stream_responses"])
                        if not script_settings["text_model_gen_settings"]["stream_responses"]:
                            chat_response_data: dict = chat_response.json()
                            if "error" not in chat_response_data:
                                model_message: str = chat_response_data["choices"][0]["message"]["content"]
                                if append_message(TEXT_MODEL_CHAT_ROLES[2], strip_thoughts(model_message)):
                                    print(f"\nMODEL: {model_message}\n")
                            else:
                                match chat_response_data["error"]["message"]:
                                    case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                        print("\nMODEL: Your message exceeds the available context size. Try increasing the context size or enable Context Shift.", end="")
                                    case "Failed to load image or audio file":
                                        print("\nMODEL: Cannot read malformed file.", end="")
                                    case _:
                                        print("\nMODEL: An error occurred.", end="")
                                print(" This message won't be added to the context.\n")
                                text_model_message_history.pop()
                        else:
                            model_message_buffer: str = ""

                            # Streaming code based on: https://gist.github.com/ggorlen/7c944d73e27980544e29aa6de1f2ac54
                            print("\nMODEL: ", end="")
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
                                            print("Your message exceeds the available context size. Try increasing the context size or enable Context Shift.", end="")
                                        case _:
                                            print("An error occurred.", end="")
                                    print(" This message won't be added to the context.", end="")
                                    text_model_message_history.pop()
                                    break
                                elif decoded_line.startswith("{\"error\":"):
                                    match json.loads(decoded_line)["error"]["message"]:
                                        case "Failed to load image or audio file":
                                            print("Cannot read malformed file.", end="")
                                        case _:
                                            print("An error occurred.", end="")
                                    print(" This message won't be added to the context.", end="")
                                    text_model_message_history.pop()
                            if model_message_buffer != "":
                                append_message(TEXT_MODEL_CHAT_ROLES[2], strip_thoughts(model_message_buffer))
                            print("\n")
                    except requests.exceptions.ConnectionError:
                        print("Text model server was closed")
                        break
                    except requests.exceptions.ChunkedEncodingError:
                        print("\nText model server was closed")
                        break
                else:
                    print("Cannot send empty messages!")
        elif script_settings["script_mode"] == SCRIPT_MODES[1]: # Autocomplete Mode
            prompt: str = input("> ")
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
                        print(f"{prompt}{text_response_data["content"]}\n")
                    else:
                        match text_response_data["error"]["message"]:
                            case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                print("Your prompt exceeds the available context size. Try increasing context size or enable Context Shift.\n")
                            case _:
                                print("An error occurred.\n")
                else:
                    printed_prompt: bool = False
                    for line in text_response.iter_lines():
                        decoded_line: str = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            if not printed_prompt:
                                printed_prompt = True
                                print(prompt, end="")
                            print(json.loads(line[len("data: "):])["content"], end="", flush=True)
                        elif decoded_line.startswith("error: "):
                            match json.loads(line[len("error: "):])["message"]:
                                case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                    print("Your prompt exceeds the available context size. Try increasing context size or enable Context Shift.", end="")
                                case _:
                                    print("An error occurred.", end="")
                            break
                    print("\n")
            except requests.exceptions.ConnectionError:
                print("Text model server was closed")
                break
            except requests.exceptions.ChunkedEncodingError:
                print("\nText model server was closed")
                break