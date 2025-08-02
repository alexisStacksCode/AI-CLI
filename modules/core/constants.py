from typing import Any


VERSION: str = "2.0.0-dev2"
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
