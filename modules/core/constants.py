from typing import Any


VERSION: str = "2.0.0-dev"
TEXT_MODEL_GEN_PARAM_MAP: dict[str, dict[str, str | None]] = {
    "temperature": {
        "internal": "temperature",
        "llama_server": "temperature",
    },
    "dynamic_temperature_range": {
        "internal": None,
        "llama_server": "dynatemp_range",
    },
    "dynamic_temperature_exponent": {
        "internal": None,
        "llama_server": "dynatemp_exponent",
    },
    "top_k": {
        "internal": "top_k",
        "llama_server": "top_k",
    },
    "top_p": {
        "internal": "top_p",
        "llama_server": "top_p",
    },
    "min_p": {
        "internal": "min_p",
        "llama_server": "min_p",
    },
    "typical_p": {
        "internal": "typical_p",
        "llama_server": "typical_p",
    },
    "tail_free_sampling": {
        "internal": "tfs_z",
        "llama_server": None,
    },
    "mirostat_mode": {
        "internal": "mirostat_mode",
        "llama_server": "mirostat",
    },
    "mirostat_tau": {
        "internal": "mirostat_tau",
        "llama_server": "mirostat_tau",
    },
    "mirostat_eta": {
        "internal": "mirostat_eta",
        "llama_server": "mirostat_eta",
    },
    "repetition_penalty": {
        "internal": "repeat_penalty",
        "llama_server": "repeat_penalty",
    },
    "repetition_penalty_range": {
        "internal": None,
        "llama_server": "repeat_last_n",
    },
    "presence_penalty": {
        "internal": "presence_penalty",
        "llama_server": "presence_penalty",
    },
    "frequency_penalty": {
        "internal": "frequency_penalty",
        "llama_server": "frequency_penalty",
    },
    "dry_base": {
        "internal": None,
        "llama_server": "dry_base",
    },
    "dry_multiplier": {
        "internal": None,
        "llama_server": "dry_multiplier",
    },
    "dry_allowed_length": {
        "internal": None,
        "llama_server": "dry_allowed_length",
    },
    "dry_penalty_range": {
        "internal": None,
        "llama_server": "dry_penalty_last_n",
    },
    "xtc_threshold": {
        "internal": None,
        "llama_server": "xtc_threshold",
    },
    "xtc_probability": {
        "internal": None,
        "llama_server": "xtc_probability",
    },
    "max_tokens": {
        "internal": "max_tokens",
        "llama_server": "n_predict",
    }
}
IMAGE_MODEL_GEN_PARAMS_SCHEMA: dict[str, dict[str, Any]] = {
    "posprompt": {
        "type": str,
        "maps_to": {
            "internal": "prompt",
            "sd_webui": "prompt",
            "swarmui": "prompt",
            "koboldcpp": "prompt",
        },
    },
    "negprompt": {
        "type": str,
        "maps_to": {
            "internal": "negative_prompt",
            "sd_webui": "negative_prompt",
            "swarmui": "negativeprompt",
            "koboldcpp": "negative_prompt",
        },
        "default_value": "",
    },
    "width": {
        "type": int,
        "maps_to": {
            "internal": "width",
            "sd_webui": "width",
            "swarmui": "width",
            "koboldcpp": "width",
        },
        "default_value": 512,
        "min_value": 256,
        "max_value": 4096,
    },
    "height": {
        "type": int,
        "maps_to": {
            "internal": "height",
            "sd_webui": "height",
            "swarmui": "height",
            "koboldcpp": "height",
        },
        "default_value": 512,
        "min_value": 256,
        "max_value": 4096,
    },
    "steps": {
        "type": int,
        "maps_to": {
            "internal": "sample_steps",
            "sd_webui": "steps",
            "swarmui": "steps",
            "koboldcpp": "steps",
        },
        "default_value": 20,
        "min_value": 1,
        "max_value": 100,
    },
    "cfgscale": {
        "type": float,
        "maps_to": {
            "internal": "cfg_scale",
            "sd_webui": "cfg_scale",
            "swarmui": "cfgscale",
            "koboldcpp": "cfg_scale",
        },
        "default_value": 5.0,
        "min_value": 0.0,
        "max_value": 20.0,
    },
    "tiling": {
        "type": bool,
        "maps_to": {
            "internal": None,
            "sd_webui": "tiling",
            "swarmui": None,
            "koboldcpp": None,
        },
        "default_value": False,
    },
    "unloadmodel": {
        "type": bool,
        "maps_to": {
            "internal": "unload_model",
            "sd_webui": None,
            "swarmui": None,
            "koboldcpp": None,
        },
        "default_value": False,
    },
}
IMAGE_MODEL_INTERNAL_INIT_PARAMS_SCHEMA: dict[str, dict[str, Any]] = {
    "modelpath": {
        "type": str,
        "maps_to": "model_path",
    },
    "modeltype": {
        "type": str,
        "maps_to": "model_type",
        "values": [
            "sd",
            "flux",
        ],
    },
    "cliplpath": {
        "type": str,
        "maps_to": "clip_l_path",
        "default_value": "",
    },
    "clipgpath": {
        "type": str,
        "maps_to": "clip_g_path",
        "default_value": "",
    },
    "t5xxlpath": {
        "type": str,
        "maps_to": "t5xxl_path",
        "default_value": "",
    },
    "vaepath": {
        "type": str,
        "maps_to": "vae_path",
        "default_value": "",
    },
    "taesdpath": {
        "type": str,
        "maps_to": "taesd_path",
        "default_value": "",
    },
    "loradirpath": {
        "type": str,
        "maps_to": "lora_model_dir",
        "default_value": "",
    },
    "vaetiling": {
        "type": bool,
        "maps_to": "vae_tiling",
        "default_value": False,
    },
    "clipcpu": {
        "type": bool,
        "maps_to": "keep_clip_on_cpu",
        "default_value": False,
    },
    "vaecpu": {
        "type": bool,
        "maps_to": "keep_vae_on_cpu",
        "default_value": False,
    },
    "flashattention": {
        "type": bool,
        "maps_to": "diffusion_flash_attn",
        "default_value": False,
    },
}
