import os
import subprocess
import base64
import json
import time
import datetime
import requests
import validators
import opengpt_constants
import opengpt_utils

if __name__ == "__main__":
    script_settings: dict = {
        "script_mode": "chat",
        "server_init_settings": {
            "exe_startup_behavior": "subprocess",
            "port": 5005,
            "high_priority": False,
            "use_mmap": False,
            "use_mlock": False,
            "use_avx2": True,
            "gpu_acceleration": "cuda",
            "gpu_layers": -1,
        },
        "server_init_lm_settings": {
            "load_mmproj": True,
            "mmproj_uses_gpu": True,
            "use_flash_attention": True,
            "use_sliding_window_attention": False,
            "blas_batch_size": 512,
            "kv_cache_data_type": "f16",
            "context_processing": "context_shift",
            "use_fast_forward": True,
            "context_size": 8192,
        },
        "server_init_sd_settings": {
            "enable": False,
            "use_vae_tiling": True,
            "quantize_safetensors_on_startup": False,
        },
        "text_model_settings": {
            "disable_url_attachments": False,
            "stream_responses": True,
            "chat_show_thoughts_in_nonstreaming_mode": True,
            "chat_include_thoughts_in_history": False,
            "autocomplete_max_tokens": 128,
            "temperature": 0.75,
            "temperature_smoothing_factor": 0.0,
            "dynamic_temperature_range": 0.0,
            "dynamic_temperature_exponent": 1.0,
            "top_a": 0.0,
            "top_k": 100,
            "top_p": 0.92,
            "min_p": 0.0,
            "top_n_sigma": 0.0,
            "typical_sampling": 1.0,
            "tail_free_sampling": 1.0,
            "mirostat_mode": "none",
            "mirostat_tau": 5.0,
            "mirostat_eta": 0.1,
            "dry_base": 1.75,
            "dry_multiplier": 0.0,
            "dry_allowed_length": 2,
            "xtc_threshold": 0.2,
            "xtc_probability": 0.0,
            "repetition_penalty": 1.07,
            "repetition_penalty_range": 360,
            "repetition_penalty_slope": 0.7,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
        },
        "image_model_settings": {
            "open_image_on_gen": False,
            "cfg_scale": 5,
            "steps": 20,
            "width": 512,
            "height": 512,
            "seed": -1,
            "clip_skip": -1,
            "sampler_name": "Euler a",
        },
    }
    server_url: str = "http://localhost:"
    is_server_active: bool = False
    text_model_id: str = ""
    text_model_context_size: int = 0
    text_model_modalities: dict[str, bool] = {
        "vision": False,
        "audio": False,
    }
    text_model_chat_message_history: list[dict] = []
    can_generate_images_in_chat: bool = False

    def append_message(role: str, message: str, _file_path: str="") -> bool:
        if role not in opengpt_constants.TEXT_MODEL_CHAT_ROLES:
            opengpt_utils.new_print(f"Cannot add messages from role '{role}' to the context", opengpt_constants.PRINT_COLORS["error"])
            return False

        is_message_empty: bool = message.rstrip() == ""
        file_path_length: int = len(_file_path)
        filename: str = os.path.basename(_file_path)
        file_extension: str = opengpt_utils.get_file_extension(_file_path, False)
        does_file_exist: bool = os.path.exists(_file_path)
        is_file_valid_url: validators.ValidationError | bool = validators.url(_file_path)
        is_file_generic_url: bool = opengpt_utils.is_generic_url(_file_path)

        if script_settings["text_model_settings"]["disable_url_attachments"] and role == "user" and is_file_valid_url:
            opengpt_utils.new_print("URL attachments are disabled", opengpt_constants.PRINT_COLORS["warning"])
            return append_message(role, message)

        if (is_file_valid_url and is_file_generic_url) or filename in opengpt_constants.TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES or file_extension in opengpt_constants.TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS:
            if not is_file_generic_url:
                if not does_file_exist:
                    opengpt_utils.new_print("File not found", opengpt_constants.PRINT_COLORS["warning"])
                    return append_message(role, message)

                try:
                    with open(_file_path, "rt") as _file:
                        text_model_chat_message_history.append({
                            "role": role,
                            "content": f"`{filename}`:\n\n```\n{_file.read()}\n```{f"\n\n{message}" if not is_message_empty else ""}",
                        })
                except UnicodeDecodeError:
                    opengpt_utils.new_print("File is unreadable", opengpt_constants.PRINT_COLORS["warning"])
                    return append_message(role, message)
            else:
                try:
                    url_content_response: requests.Response = requests.get(_file_path)
                    url_content_response.raise_for_status()
                    text_model_chat_message_history.append({
                        "role": role,
                        "content": f"`{_file_path}`:\n\n```\n{url_content_response.text}\n```{f"\n\n{message}" if not is_message_empty else ""}",
                    })
                except requests.HTTPError:
                    opengpt_utils.new_print("URL not found", opengpt_constants.PRINT_COLORS["warning"])
                    return append_message(role, message)
                except requests.ConnectionError:
                    opengpt_utils.new_print("Failed to resolve URL", opengpt_constants.PRINT_COLORS["warning"])
                    return append_message(role, message)
            return True
        elif file_extension in opengpt_constants.TEXT_MODEL_ATTACHMENT_IMAGE_EXTENSIONS:
            if not is_file_valid_url and not does_file_exist:
                opengpt_utils.new_print("File not found", opengpt_constants.PRINT_COLORS["warning"])
                return append_message(role, message)

            if not text_model_modalities["vision"]:
                opengpt_utils.new_print(f"Vision is not enabled for '{text_model_id}'", opengpt_constants.PRINT_COLORS["warning"])
                return append_message(role, message)

            text_model_chat_message_history.append({
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": opengpt_utils.get_image_data(_file_path) if not is_file_valid_url else _file_path,
                        },
                    },
                ]
            })
            return True
        elif file_extension in opengpt_constants.TEXT_MODEL_ATTACHMENT_AUDIO_EXTENSIONS:
            if not does_file_exist:
                opengpt_utils.new_print("File not found", opengpt_constants.PRINT_COLORS["warning"])
                return append_message(role, message)

            if not text_model_modalities["audio"]:
                opengpt_utils.new_print(f"Audio is not enabled for '{text_model_id}'", opengpt_constants.PRINT_COLORS["warning"])
                return append_message(role, message)

            text_model_chat_message_history.append({
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "input_audio",
                        "input_audio": opengpt_utils.get_audio_data(_file_path),
                    },
                ]
            })
            return True

        if role == "user" and is_message_empty and file_path_length == 0:
            return False

        if file_path_length > 0:
            opengpt_utils.new_print("File does not exist or is unsupported", opengpt_constants.PRINT_COLORS["warning"])
            if is_message_empty:
                return False
        text_model_chat_message_history.append({
            "role": role,
            "content": message,
        })
        return True

    def get_current_script_mode() -> str:
        for script_mode in opengpt_constants.SCRIPT_MODES:
            if script_mode == script_settings["script_mode"]:
                return script_mode.capitalize()
        return "Unknown"

    def get_server_status() -> bool:
        try:
            requests.get(f"{server_url}/api/extra/version")
            return True
        except requests.ConnectionError:
            return False

    # noinspection PyShadowingNames
    def is_text_model_multimodal() -> bool:
        for value in text_model_modalities.values():
            if value:
                return True
        return False

    def construct_text_model_gen_parameters() -> dict:
        return {
            "temperature": script_settings["text_model_settings"]["temperature"],
            "smoothing_factor": script_settings["text_model_settings"]["temperature_smoothing_factor"],
            "dynatemp_range": script_settings["text_model_settings"]["dynamic_temperature_range"],
            "dynatemp_exponent": script_settings["text_model_settings"]["dynamic_temperature_exponent"],
            "top_a": script_settings["text_model_settings"]["top_a"],
            "top_k": script_settings["text_model_settings"]["top_k"],
            "top_p": script_settings["text_model_settings"]["top_p"],
            "min_p": script_settings["text_model_settings"]["min_p"],
            "nsigma": script_settings["text_model_settings"]["top_n_sigma"],
            "typical": script_settings["text_model_settings"]["typical_sampling"],
            "tfs": script_settings["text_model_settings"]["tail_free_sampling"],
            "mirostat": opengpt_constants.TEXT_MODEL_MIROSTAT_MODES[script_settings["text_model_settings"]["mirostat_mode"]],
            "mirostat_tau": script_settings["text_model_settings"]["mirostat_tau"],
            "mirostat_eta": script_settings["text_model_settings"]["mirostat_eta"],
            "dry_base": script_settings["text_model_settings"]["dry_base"],
            "dry_multiplier": script_settings["text_model_settings"]["dry_multiplier"],
            "dry_allowed_length": script_settings["text_model_settings"]["dry_allowed_length"],
            "xtc_threshold": script_settings["text_model_settings"]["xtc_threshold"],
            "xtc_probability": script_settings["text_model_settings"]["xtc_probability"],
            "rep_pen": script_settings["text_model_settings"]["repetition_penalty"],
            "rep_pen_range": script_settings["text_model_settings"]["repetition_penalty_range"],
            "rep_pen_slope": script_settings["text_model_settings"]["repetition_penalty_slope"],
            "presence_penalty": script_settings["text_model_settings"]["presence_penalty"],
            "frequency_penalty": script_settings["text_model_settings"]["frequency_penalty"],
        }

    # noinspection PyShadowingNames
    def get_text_model_chat_total_tokens() -> int:
        tokens: int = 0
        for message in text_model_chat_message_history:
            payload: dict = {
                "prompt": message["content"] if type(message["content"]) == str else message["content"][0]["text"],
            }
            token_count_response: requests.Response = requests.get(f"{server_url}/api/extra/tokencount", json=payload)
            tokens += token_count_response.json()["value"]
        return tokens

    def validate_image_model_optional_file(path: str) -> str:
        if len(path) > 0 and (not os.path.exists(path) or opengpt_utils.get_file_extension(path, False) != ".safetensors"):
            opengpt_utils.new_print("File does not exist or its extension isn't .safetensors", opengpt_constants.PRINT_COLORS["warning"])
            return ""
        return path

    if os.path.exists(opengpt_constants.SCRIPT_SETTINGS_PATH):
        with open(opengpt_constants.SCRIPT_SETTINGS_PATH, "rt") as file:
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
                                opengpt_utils.new_print(f"Malformed setting '{key}.{subkey}'", opengpt_constants.PRINT_COLORS["warning"])
                else:
                    opengpt_utils.new_print(f"Malformed setting '{key}'", opengpt_constants.PRINT_COLORS["warning"])

            # Validate script_mode.
            if script_settings["script_mode"] not in opengpt_constants.SCRIPT_MODES:
                script_settings["script_mode"] = "chat"

            # Validate server_init_settings.
            if script_settings["server_init_settings"]["exe_startup_behavior"] not in opengpt_constants.SERVER_STARTUP_BEHAVIOR_OPTIONS:
                script_settings["server_init_settings"]["exe_startup_behavior"] = "subprocess"
            script_settings["server_init_settings"]["port"] = opengpt_utils.clamp_int(script_settings["server_init_settings"]["port"], 1000, 9999)
            if script_settings["server_init_settings"]["gpu_acceleration"] not in opengpt_constants.SERVER_GPU_ACCELERATION_OPTIONS:
                script_settings["server_init_settings"]["gpu_acceleration"] = "cuda"
            script_settings["server_init_settings"]["gpu_layers"] = max(script_settings["server_init_settings"]["gpu_layers"], -1)

            # Validate server_init_lm_settings.
            script_settings["server_init_lm_settings"]["blas_batch_size"] = max(script_settings["server_init_lm_settings"]["blas_batch_size"], -1)
            if script_settings["server_init_lm_settings"]["kv_cache_data_type"] not in opengpt_constants.SERVER_LM_KV_CACHE_DATA_TYPES:
                script_settings["server_init_lm_settings"]["kv_cache_data_type"] = "f16"
            if script_settings["server_init_lm_settings"]["context_processing"] not in opengpt_constants.SERVER_LM_CONTEXT_PROCESSING_OPTIONS:
                script_settings["server_init_lm_settings"]["context_processing"] = "context_shift"
            script_settings["server_init_lm_settings"]["context_size"] = max(script_settings["server_init_lm_settings"]["context_size"], 256)

            # Validate text_model_settings.
            script_settings["text_model_settings"]["autocomplete_max_tokens"] = max(script_settings["text_model_settings"]["autocomplete_max_tokens"], 1)
            script_settings["text_model_settings"]["temperature"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["temperature"], 0.0, 2.0)
            script_settings["text_model_settings"]["temperature_smoothing_factor"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["temperature_smoothing_factor"], 0.0, 10.0)
            script_settings["text_model_settings"]["dynamic_temperature_range"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["dynamic_temperature_range"], -5.0, 5.0)
            script_settings["text_model_settings"]["top_a"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["top_a"], 0.0, 1.0)
            script_settings["text_model_settings"]["top_k"] = opengpt_utils.clamp_int(script_settings["text_model_settings"]["top_k"], 0, 100)
            script_settings["text_model_settings"]["top_p"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["top_p"], 0.0, 1.0)
            script_settings["text_model_settings"]["min_p"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["min_p"], 0.0, 1.0)
            script_settings["text_model_settings"]["top_n_sigma"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["top_n_sigma"], 0.0, 5.0)
            script_settings["text_model_settings"]["typical_sampling"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["typical_sampling"], 0.0, 1.0)
            script_settings["text_model_settings"]["tail_free_sampling"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["tail_free_sampling"], 0.0, 1.0)
            if script_settings["text_model_settings"]["mirostat_mode"] not in opengpt_constants.TEXT_MODEL_MIROSTAT_MODES:
                script_settings["text_model_settings"]["mirostat_mode"] = "none"
            script_settings["text_model_settings"]["mirostat_tau"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["mirostat_tau"], 0.0, 30.0)
            script_settings["text_model_settings"]["mirostat_eta"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["mirostat_eta"], 0.0, 10.0)
            script_settings["text_model_settings"]["dry_base"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["dry_base"], 0.0, 8.0)
            script_settings["text_model_settings"]["dry_multiplier"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["dry_multiplier"], 0.0, 100.0)
            script_settings["text_model_settings"]["dry_allowed_length"] = opengpt_utils.clamp_int(script_settings["text_model_settings"]["dry_allowed_length"], 0, 100)
            script_settings["text_model_settings"]["xtc_threshold"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["xtc_threshold"], 0.0, 1.0)
            script_settings["text_model_settings"]["xtc_probability"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["xtc_probability"], 0.0, 1.0)
            script_settings["text_model_settings"]["repetition_penalty"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["repetition_penalty"], 1.0, 2.0)
            script_settings["text_model_settings"]["repetition_penalty_range"] = max(script_settings["text_model_settings"]["repetition_penalty_range"], 0)
            script_settings["text_model_settings"]["repetition_penalty_slope"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["repetition_penalty_slope"], 0.0, 20.0)
            script_settings["text_model_settings"]["presence_penalty"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["presence_penalty"], -2.0, 2.0)
            script_settings["text_model_settings"]["frequency_penalty"] = opengpt_utils.clamp_float(script_settings["text_model_settings"]["frequency_penalty"], -2.0, 2.0)

            # TODO: implement image_model_settings validation
    with open(opengpt_constants.SCRIPT_SETTINGS_PATH, "wt") as file:
        json.dump(script_settings, file, indent=4)

    server_url += str(script_settings["server_init_settings"]["port"])
    opengpt_utils.new_print(f"Script will run in {get_current_script_mode()} Mode\n", opengpt_constants.PRINT_COLORS["special"])

    is_server_active = get_server_status()
    if not is_server_active:
        while True:
            koboldcpp_dir_path: str = opengpt_utils.strip_leading_and_trailing_quotes(input("Enter the path to KoboldCpp: "))
            koboldcpp_path: str = ""
            for server_filename in opengpt_constants.SERVER_FILENAMES:
                found_koboldcpp_path: str = f"{koboldcpp_dir_path}{server_filename}"
                if os.path.exists(found_koboldcpp_path):
                    koboldcpp_path = found_koboldcpp_path
                    break
            if koboldcpp_path != "" and os.path.exists(koboldcpp_path):
                break
            opengpt_utils.new_print(f"Directory does not exist or KoboldCpp was not found", opengpt_constants.PRINT_COLORS["error"])

        while True:
            text_model_path: str = opengpt_utils.strip_leading_and_trailing_quotes(input("Enter a text model path: "))
            text_model_extension: str = opengpt_utils.get_file_extension(text_model_path, False)
            if os.path.exists(text_model_path) and text_model_extension in opengpt_constants.TEXT_MODEL_EXTENSIONS:
                break
            opengpt_utils.new_print("File does not exist or is not a text model", opengpt_constants.PRINT_COLORS["error"])

        image_model_path: str = ""
        image_model_extension: str = ""
        image_model_t5_xxl_path: str = ""
        image_model_clip_l_path: str = ""
        image_model_clip_g_path: str = ""
        image_model_vae_path: str = ""
        image_model_lora_path: str = ""
        image_model_lora_multiplier: float = 0.5
        if script_settings["server_init_sd_settings"]["enable"]:
            while True:
                image_model_path = opengpt_utils.strip_leading_and_trailing_quotes(input("Enter an image model path: "))
                image_model_extension = opengpt_utils.get_file_extension(image_model_path, False)
                if os.path.exists(image_model_path) and image_model_extension in opengpt_constants.IMAGE_MODEL_EXTENSIONS:
                    break
                opengpt_utils.new_print("File does not exist or is not an image model", opengpt_constants.PRINT_COLORS["error"])

            image_model_t5_xxl_path = validate_image_model_optional_file(opengpt_utils.strip_leading_and_trailing_quotes(input("Enter a T5-XXL model path (optional): ")))
            image_model_clip_l_path = validate_image_model_optional_file(opengpt_utils.strip_leading_and_trailing_quotes(input("Enter a Clip-L model path (optional): ")))
            image_model_clip_g_path = validate_image_model_optional_file(opengpt_utils.strip_leading_and_trailing_quotes(input("Enter a Clip-G model path (optional): ")))
            image_model_vae_path = validate_image_model_optional_file(opengpt_utils.strip_leading_and_trailing_quotes(input("Enter a VAE path (optional): ")))

            if image_model_extension == ".safetensors":
                image_model_lora_path = validate_image_model_optional_file(opengpt_utils.strip_leading_and_trailing_quotes(input("Enter an image model LoRA path (optional): ")))
                while True:
                    try:
                        image_model_lora_multiplier = opengpt_utils.clamp_float(float(input("Enter the LoRA multiplier (0.0-1.0): ")), 0.0, 1.0)
                        break
                    except ValueError:
                        print("Invalid value")

        opengpt_utils.new_print("Starting server", opengpt_constants.PRINT_COLORS["success"])
        text_model_mmproj_path: str = f"{text_model_path.removesuffix(".gguf")}-mmproj.gguf" if text_model_extension == ".gguf" else ""
        arguments: str = opengpt_utils.construct_arguments([
            "--singleinstance",
            "--skiplauncher",
            f"--port {script_settings["server_init_settings"]["port"]}",
            "--highpriority" if script_settings["server_init_settings"]["high_priority"] else "",
            "--usemmap" if script_settings["server_init_settings"]["use_mmap"] else "",
            "--usemlock" if script_settings["server_init_settings"]["use_mlock"] else "",
            "--noavx2" if not script_settings["server_init_settings"]["use_avx2"] else "",
            "--usecpu" if script_settings["server_init_settings"]["gpu_acceleration"] == "none" else "",
            "--usecublas normal" if script_settings["server_init_settings"]["gpu_acceleration"] == "cuda" else "",
            "--usecublas lowvram" if script_settings["server_init_settings"]["gpu_acceleration"] == "cuda_low_vram" else "",
            "--usehipblas normal" if script_settings["server_init_settings"]["gpu_acceleration"] == "hip" else "",
            "--usehipblas lowvram" if script_settings["server_init_settings"]["gpu_acceleration"] == "hip_low_vram" else "",
            "--usevulkan" if script_settings["server_init_settings"]["gpu_acceleration"] == "vulkan" else "",
            "--useclblast 0 0" if script_settings["server_init_settings"]["gpu_acceleration"] == "opencl" else "",
            f"--gpulayers {script_settings["server_init_settings"]["gpu_layers"]}",
            "--mmprojcpu" if not script_settings["server_init_lm_settings"]["mmproj_uses_gpu"] else "",
            "--flashattention" if script_settings["server_init_lm_settings"]["use_flash_attention"] else "",
            "--useswa" if script_settings["server_init_lm_settings"]["use_sliding_window_attention"] else "",
            f"--blasbatchsize {script_settings["server_init_lm_settings"]["blas_batch_size"]}",
            f"--quantkv {opengpt_constants.SERVER_LM_KV_CACHE_DATA_TYPES[script_settings["server_init_lm_settings"]["kv_cache_data_type"]]}",
            "--noshift" if script_settings["server_init_lm_settings"]["context_processing"] == "none" or script_settings["server_init_lm_settings"]["context_processing"] == "smart_context" else "",
            "--smartcontext" if script_settings["server_init_lm_settings"]["context_processing"] == "smart_context" else "",
            "--nofastforward" if not script_settings["server_init_lm_settings"]["use_fast_forward"] else "",
            f"--contextsize {script_settings["server_init_lm_settings"]["context_size"]}",
            f"--defaultgenamt {script_settings["server_init_lm_settings"]["context_size"]}",
            "--sdnotile" if script_settings["server_init_sd_settings"]["enable"] and not script_settings["server_init_sd_settings"]["use_vae_tiling"] else "",
            "--sdquant" if script_settings["server_init_sd_settings"]["enable"] and script_settings["server_init_sd_settings"]["quantize_safetensors_on_startup"] and image_model_extension == ".safetensors" else "",
            f"--model \"{text_model_path}\"",
            f"--mmproj \"{text_model_mmproj_path}\"" if script_settings["server_init_lm_settings"]["load_mmproj"] and text_model_mmproj_path != "" and os.path.exists(text_model_mmproj_path) else "",
            f"--sdmodel \"{image_model_path}\"" if script_settings["server_init_sd_settings"]["enable"] else "",
            f"--sdt5xxl \"{image_model_t5_xxl_path}\"" if script_settings["server_init_sd_settings"]["enable"] and image_model_t5_xxl_path != "" else "",
            f"--sdclipl \"{image_model_clip_l_path}\"" if script_settings["server_init_sd_settings"]["enable"] and image_model_clip_l_path != "" else "",
            f"--sdclipg \"{image_model_clip_g_path}\"" if script_settings["server_init_sd_settings"]["enable"] and image_model_clip_g_path != "" else "",
            f"--sdvae \"{image_model_vae_path}\"" if script_settings["server_init_sd_settings"]["enable"] and image_model_vae_path != "" else "",
            f"--sdlora \"{image_model_lora_path}\"" if script_settings["server_init_sd_settings"]["enable"] and image_model_lora_path != "" else "",
            f"--sdloramult {image_model_lora_multiplier}" if script_settings["server_init_sd_settings"]["enable"] and image_model_lora_path != "" else "",
        ])
        match opengpt_utils.get_file_extension(koboldcpp_path, False):
            case ".exe":
                match script_settings["server_init_settings"]["exe_startup_behavior"]:
                    case "separate_process":
                        os.startfile(koboldcpp_path, arguments=arguments)
                    case "subprocess":
                        subprocess.Popen(f"{koboldcpp_path}{f" {arguments}" if len(arguments) > 0 else ""}")
            case ".py":
                subprocess.Popen(f"python {koboldcpp_path} {arguments}")

    server_checks: int = 0
    printed_server_check_warning: bool = False
    while True:
        if not is_server_active:
            if server_checks == opengpt_constants.MAX_SERVER_CHECKS * 0.5 and not printed_server_check_warning:
                printed_server_check_warning = True
                opengpt_utils.new_print("Server is still loading...", opengpt_constants.PRINT_COLORS["warning"])
            if server_checks > opengpt_constants.MAX_SERVER_CHECKS:
                opengpt_utils.new_print("Server connection timed out", opengpt_constants.PRINT_COLORS["error"])
                exit()

            server_checks += 1
            is_server_active = get_server_status()
        else:
            try:
                text_model_info_response: requests.Response = requests.get(f"{server_url}/api/v1/model")
                text_model_id = text_model_info_response.json()["result"].removeprefix("koboldcpp/")
                text_model_context_size_response: requests.Response = requests.get(f"{server_url}/api/extra/true_max_context_length")
                text_model_context_size = text_model_context_size_response.json()["value"]
                version_response: requests.Response = requests.get(f"{server_url}/api/extra/version")
                version_response_data: dict = version_response.json()
                for modality in text_model_modalities.keys():
                    if modality in version_response_data:
                        text_model_modalities[modality] = version_response_data[modality]
                opengpt_utils.new_print(f"Server (Version {version_response_data["version"]}) is online", opengpt_constants.PRINT_COLORS["success"])
                opengpt_utils.new_print(f"Text Model: {text_model_id} (Context Size: {text_model_context_size}, Vision: {text_model_modalities["vision"]}, Audio: {text_model_modalities["audio"]})", opengpt_constants.PRINT_COLORS["success"])
                if version_response_data["txt2img"]:
                    image_model_info_response: requests.Response = requests.get(f"{server_url}/sdapi/v1/sd-models")

                    can_generate_images_in_chat = True
                    opengpt_utils.new_print(f"Image Model: {image_model_info_response.json()[0]["model_name"]}", opengpt_constants.PRINT_COLORS["success"])
                break
            except requests.ConnectionError:
                opengpt_utils.new_print("404", opengpt_constants.PRINT_COLORS["error"])

    # If the system prompt is specified and the script is running in Chat Mode, add it to the context.
    if script_settings["script_mode"] == "chat" and os.path.exists(opengpt_constants.TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH):
        try:
            with open(opengpt_constants.TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH, "rt") as file:
                file_content: str = file.read()
                if file_content.strip() != "":
                    append_message("system", file_content)
        except UnicodeDecodeError:
            opengpt_utils.new_print("Malformed system prompt", opengpt_constants.PRINT_COLORS["warning"], "")

    print("\n", end="")
    while True:
        match script_settings["script_mode"]:
            case "chat":
                user_message: str = input(f"{opengpt_constants.PRINT_COLORS["user_prefix"]}USER: {opengpt_constants.PRINT_COLORS["reset"]}")
                command: str = user_message.strip()

                if command == opengpt_constants.COMMAND_IMAGE_ALIAS:
                    if not can_generate_images_in_chat:
                        opengpt_utils.new_print("Image generation is unavailable", opengpt_constants.PRINT_COLORS["error"])
                        continue

                    image_positive_prompt: str = input("Enter a positive prompt: ").strip()
                    if image_positive_prompt == "":
                        opengpt_utils.new_print("Cannot generate images with an empty positive prompt", opengpt_constants.PRINT_COLORS["error"])
                        continue
                    image_negative_prompt: str = input("Enter a negative prompt (optional): ").strip()
                    opengpt_utils.new_print("Generating...", opengpt_constants.PRINT_COLORS["success"])

                    try:
                        payload: dict = {
                            "prompt": image_positive_prompt,
                            "negative_prompt": image_negative_prompt,
                        }
                        for key, value in script_settings["image_model_settings"].items():
                            if key not in opengpt_constants.IMAGE_MODEL_EXCLUDED_PAYLOAD_KEYS:
                                payload[key] = value
                        image_gen_start_time: float = time.time()
                        image_response: requests.Response = requests.post(f"{server_url}/sdapi/v1/txt2img", json=payload)

                        # Ensure that the image output directory exists.
                        try:
                            os.mkdir(opengpt_constants.IMAGE_MODEL_OUTPUT_DIR_NAME)
                        except FileExistsError:
                            pass

                        image_output_path: str = f"{opengpt_constants.IMAGE_MODEL_OUTPUT_DIR_NAME}{datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")}.png"
                        with open(image_output_path, "wb") as file:
                            file.write(base64.b64decode(image_response.json()["images"][0]))
                        if script_settings["image_model_settings"]["open_image_on_gen"]:
                            os.startfile(os.path.abspath(image_output_path))
                        model_message: str = f"Generated in {"{:.2f}".format(time.time() - image_gen_start_time)} seconds."
                        if text_model_modalities["vision"]:
                            if image_negative_prompt == "":
                                append_message("user", f"**Prompt:** {image_positive_prompt}\n\nGenerate an image using the provided prompt.")
                            else:
                                append_message("user", f"**Positive Prompt:** {image_positive_prompt}\n**Negative Prompt:** {image_negative_prompt}\n\nGenerate an image using the provided positive prompt and negative prompt.")
                            if append_message("assistant", model_message, image_output_path):
                                print(f"\n{opengpt_constants.PRINT_COLORS["model_prefix"]}MODEL: {opengpt_constants.PRINT_COLORS["reset"]}{model_message}\n")
                        else:
                            print(f"\n{opengpt_constants.PRINT_COLORS["model_prefix"]}MODEL: {opengpt_constants.PRINT_COLORS["reset"]}{model_message} This message won't be added to the context as I cannot see images.\n")
                    except requests.exceptions.ConnectionError:
                        opengpt_utils.new_print("Server was closed", opengpt_constants.PRINT_COLORS["error"])
                        exit()
                elif command == opengpt_constants.COMMAND_HELP_ALIAS:
                    opengpt_utils.new_print(f"{opengpt_constants.COMMAND_IMAGE_ALIAS} - Generate an image (requires the image model server to be online).", opengpt_constants.PRINT_COLORS["special"])
                    opengpt_utils.new_print(f"{opengpt_constants.COMMAND_ATTACH_ALIAS} - Attach a file or URL to your message (command must be at the end of your message).", opengpt_constants.PRINT_COLORS["special"])
                    opengpt_utils.new_print(f"{opengpt_constants.COMMAND_HELP_ALIAS} - Display all commands.", opengpt_constants.PRINT_COLORS["special"])
                    opengpt_utils.new_print(f"{opengpt_constants.COMMAND_EXIT_ALIAS} - Exit the application.", opengpt_constants.PRINT_COLORS["special"])
                elif command == opengpt_constants.COMMAND_EXIT_ALIAS:
                    requests.post(f"{server_url}/api/extra/shutdown")
                    break
                else:
                    file_path: str = ""

                    if command.endswith(opengpt_constants.COMMAND_ATTACH_ALIAS):
                        file_path = opengpt_utils.strip_leading_and_trailing_quotes(input("Enter a file path or URL: "))
                        user_message = user_message.removesuffix(opengpt_constants.COMMAND_ATTACH_ALIAS).rstrip()

                    # TODO: for KoboldCpp server branch, convert leftover llama.cpp stuff to KoboldCpp
                    if append_message("user", user_message, file_path):
                        if script_settings["server_init_lm_settings"]["context_processing"] == "none" and get_text_model_chat_total_tokens() >= text_model_context_size:
                            opengpt_utils.new_print("Your message exceeds the available context size. Try increasing the context size or enable Context Shift/Smart Context.", opengpt_constants.PRINT_COLORS["error"])
                            continue

                        try:
                            payload: dict = {
                                "model": text_model_id,
                                "messages": text_model_chat_message_history,
                                "stream": script_settings["text_model_settings"]["stream_responses"],
                                "max_context_length": text_model_context_size,
                            }
                            for key, value in construct_text_model_gen_parameters().items():
                                payload[key] = value

                            opengpt_utils.new_print("\nMODEL: ", opengpt_constants.PRINT_COLORS["model_prefix"], "")
                            chat_response: requests.Response = requests.post(f"{server_url}/v1/chat/completions", json=payload, stream=script_settings["text_model_settings"]["stream_responses"])
                            if not script_settings["text_model_settings"]["stream_responses"]:
                                chat_response_data: dict = chat_response.json()
                                print(chat_response_data)
                                if "error" not in chat_response_data:
                                    model_message: str = chat_response_data["choices"][0]["message"]["content"]
                                    if append_message("assistant", opengpt_utils.process_text(model_message, script_settings["text_model_settings"]["chat_include_thoughts_in_history"])):
                                        print(f"{opengpt_utils.process_text(model_message, script_settings["text_model_settings"]["chat_show_thoughts_in_nonstreaming_mode"])}\n")
                                else:
                                    match chat_response_data["error"]["message"]:
                                        case "failed to decode, ret = -1":
                                            print("Your message exceeds the available context size. Try increasing the context size or enable Context Shift.", end="")
                                        case "Failed to load image or audio file":
                                            print("This file is not encodable.", end="")
                                        case _:
                                            print("An error occurred.", end="")
                                    print(" This message won't be added to the context.\n")
                                    text_model_chat_message_history.pop()
                            else:
                                model_message_buffer: str = ""

                                # Streaming code based on: https://gist.github.com/ggorlen/7c944d73e27980544e29aa6de1f2ac54
                                for line in chat_response.iter_lines():
                                    decoded_line: str = line.decode("utf-8")
                                    if decoded_line.startswith("data: ") and not decoded_line.endswith("[DONE]"):
                                        model_message_data: dict = json.loads(line[len("data: "):])["choices"][0]

                                        if model_message_data["finish_reason"] == "length" and model_message_data["delta"]["content"] == "":
                                            text_model_chat_message_history.pop()
                                            opengpt_utils.new_print("An error occurred.", opengpt_constants.PRINT_COLORS["error"], "")
                                            break

                                        chunk: str | None = model_message_data["delta"]["content"]
                                        model_message_buffer += chunk
                                        print(chunk, end="", flush=True)
                                    elif decoded_line.startswith("error: "):
                                        match json.loads(line[len("error: "):])["message"]:
                                            case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                                opengpt_utils.new_print("Your message exceeds the available context size. Try increasing the context size or enable Context Shift.", opengpt_constants.PRINT_COLORS["error"], "")
                                            case _:
                                                opengpt_utils.new_print("An error occurred.", opengpt_constants.PRINT_COLORS["error"], "")
                                        print(" This message won't be added to the context.", end="")
                                        text_model_chat_message_history.pop()
                                        break
                                    elif decoded_line.startswith("{\"error\":"):
                                        match json.loads(decoded_line)["error"]["message"]:
                                            case "Failed to load image or audio file":
                                                opengpt_utils.new_print("This file is not encodable.", opengpt_constants.PRINT_COLORS["error"], "")
                                            case _:
                                                opengpt_utils.new_print("An error occurred.", opengpt_constants.PRINT_COLORS["error"], "")
                                        print(" This message won't be added to the context.", end="")
                                        text_model_chat_message_history.pop()
                                        break
                                if model_message_buffer != "":
                                    append_message("assistant", opengpt_utils.process_text(model_message_buffer, script_settings["text_model_settings"]["chat_include_thoughts_in_history"]))
                                print("\n")
                        except requests.exceptions.ConnectionError:
                            opengpt_utils.new_print("\nText model server was closed", opengpt_constants.PRINT_COLORS["error"])
                            break
                        except requests.exceptions.ChunkedEncodingError:
                            opengpt_utils.new_print("\nText model server was closed", opengpt_constants.PRINT_COLORS["error"])
                            break
                    else:
                        opengpt_utils.new_print("Cannot send empty messages", opengpt_constants.PRINT_COLORS["error"])
            case "autocomplete": # TODO: for KoboldCpp server branch, update this (currently broken due to various refactors and rewrites)
                prompt: str = input(f"{opengpt_constants.PRINT_COLORS["user_prefix"]}> {opengpt_constants.PRINT_COLORS["reset"]}")
                try:
                    payload: dict = {
                        "model": text_model_id,
                        "prompt": prompt,
                        "stream": script_settings["text_model_settings"]["stream_responses"],
                        "n_predict": script_settings["text_model_settings"]["autocomplete_max_tokens"],
                    }
                    for key, value in construct_text_model_gen_parameters().items():
                        payload[key] = value

                    text_response: requests.Response = requests.post(f"{server_url}/completion", json=payload, stream=script_settings["text_model_settings"]["stream_responses"])
                    if not script_settings["text_model_settings"]["stream_responses"]:
                        text_response_data: dict = text_response.json()
                        if "error" not in text_response_data:
                            opengpt_utils.new_print(f"{prompt}{text_response_data["content"]}\n", PRINT_COLORS["model_prefix"])
                        else:
                            match text_response_data["error"]["message"]:
                                case "the request exceeds the available context size. try increasing the context size or enable context shift":
                                    opengpt_utils.new_print("Your prompt exceeds the available context size. Try increasing the context size or enable Context Shift.\n", PRINT_COLORS["error"])
                                case _:
                                    opengpt_utils.new_print("An error occurred.\n", PRINT_COLORS["error"])
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
                                        opengpt_utils.new_print("Your prompt exceeds the available context size. Try increasing the context size or enable Context Shift.", PRINT_COLORS["error"], "")
                                    case _:
                                        opengpt_utils.new_print("An error occurred.", PRINT_COLORS["error"], "")
                                break
                        print("\n")
                except requests.exceptions.ConnectionError:
                    print("Text model server was closed")
                    break
                except requests.exceptions.ChunkedEncodingError:
                    print("\nText model server was closed")
                    break