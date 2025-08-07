from typing import Any
import os
import json


__data: dict[str, Any] = {
    "mode": "chat",
    "lm_backend": {
        "interface": "llama_server",
        "port": -1,
        "init": {
            "internal": {
                "gpu_layers": 999,
                "kv_uses_gpu": True,
                "use_mmap": False,
                "use_mlock": False,
                "use_flash_attention": True,
                "use_full_swa_cache": False,
                "logical_batch_size": 2048,
                "physical_batch_size": 2048,
                "context_size": 8192,
            },
            "llama_server": {
                "gpu_layers": 999,
                "mmproj_uses_gpu": True,
                "kv_uses_gpu": True,
                "use_mmap": False,
                "use_mlock": False,
                "use_flash_attention": True,
                "use_full_swa_cache": False,
                "use_unified_kv_buffer": False,
                "kv_cache_reuse_size": 256,
                "use_continuous_batching": True,
                "logical_batch_size": 2048,
                "physical_batch_size": 2048,
                "context_size": 8192,
                "use_context_shift": True,
            },
        },
        "gen": {
            "response_stream": "sse",
            "temperature": 0.8,
            "dynamic_temperature_range": 0.0,
            "dynamic_temperature_exponent": 1.0,
            "top_k": 40,
            "top_p": 0.95,
            "min_p": 0.05,
            "typical_p": 1.0,
            "tail_free_sampling": 1.0,
            "mirostat_mode": 0,
            "mirostat_tau": 5.0,
            "mirostat_eta": 0.1,
            "repetition_penalty": 1.1,
            "repetition_penalty_range": 64,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "dry_base": 1.75,
            "dry_multiplier": 0.0,
            "dry_allowed_length": 2,
            "dry_penalty_range": -1,
            "xtc_threshold": 0.1,
            "xtc_probability": 0.0,
            "max_tokens": 128,
        },
    },
    "im_backend": {
        "interface": "swarmui",
        "port": -1,
        "open_output_on_gen": False,
    },
}


def load() -> None:
    global __data

    settings_file = "data/settings.json"

    if os.path.exists(settings_file):
        try:
            with open(settings_file, "rt") as file:
                __data = json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings from {settings_file}: {e}")
            print("Using default settings.")
    else:
        print(f"Settings file {settings_file} not found. Using default settings.")


def save() -> None:
    settings_file = "data/settings.json"

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    try:
        with open(settings_file, "wt") as file:
            json.dump(__data, file, indent=4)
    except IOError as e:
        print(f"Error saving settings to {settings_file}: {e}")


def get(path: str) -> Any:
    keys = path.split("/")
    current = __data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return None
