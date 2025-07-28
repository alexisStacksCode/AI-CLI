from typing import Any
from colorama import Fore

REPOSITORY_OWNER: str = "alexisStacksCode"
REPOSITORY_NAME: str = "OpenGPT-CLI"
VERSION: str = "v1.1.0"
AI_MODES: list[str] = [
    "chat",
    "autocomplete",
]
SETTINGS_PATH: str = "data/settings.json"
SERVER_FILENAME: str = "llama-server.exe"
PRINT_COLORS: dict[str, str] = {
    "reset": Fore.RESET,
    "special": Fore.LIGHTCYAN_EX,
    "user_prefix": Fore.LIGHTBLUE_EX,
    "model_prefix": Fore.LIGHTMAGENTA_EX,
    "success": Fore.LIGHTGREEN_EX,
    "warning": Fore.LIGHTYELLOW_EX,
    "error": Fore.LIGHTRED_EX,
}
TEXT_MODEL_EXTENSION: str = ".gguf"
TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH: str = "data/chat_system_prompt.txt"
TEXT_MODEL_KV_CACHE_DATA_TYPES: list[str] = [
    "f32",
    "f16",
    "bf16",
]
TEXT_MODEL_RESPONSE_STREAM_OPTIONS: list[str] = [
    "off",
    "sse",
    "typewriter",
]
TEXT_MODEL_CHAT_ROLES: list[str] = [
    "system",
    "user",
    "assistant",
]
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

    # Extensible Markup Language (also identifiable as XHTML)
    ".xml",

    # YAML Ain't Markup Language
    ".yaml",
    ".yml",

    # Standard Generalized Markup Language
    ".sgml",

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

    # HTML5 & XHTML
    ".html",
    ".htm",
    ".xhtml",
    ".xht",

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
IMAGE_MODEL_OUTPUT_DIR_NAME: str = "image_output/"
IMAGE_MODEL_AVAILABLE_GEN_PARAMS: dict[str, dict[str, Any]] = {
    "posprompt": {
        "type": str,
        "maps_to": "prompt",
    },
    "negprompt": {
        "type": str,
        "maps_to": "negativeprompt",
        "default_value": "",
    },
    "width": {
        "type": int,
        "maps_to": "width",
        "default_value": 512,
        "min_value": 256,
        "max_value": 4096,
    },
    "height": {
        "type": int,
        "maps_to": "height",
        "default_value": 512,
        "min_value": 256,
        "max_value": 4096,
    },
    "steps": {
        "type": int,
        "maps_to": "steps",
        "default_value": 20,
        "min_value": 0,
        "max_value": 100,
    },
    "cfgscale": {
        "type": float,
        "maps_to": "cfgscale",
        "default_value": 5.0,
        "min_value": 0.0,
        "max_value": 20.0,
    },
    "sampler": {
        "type": str,
        "maps_to": "sampler",
        "default_value": "euler",
        "values": [
            "euler",
            "euler_ancestral",
            "heun",
            "heunpp2",
            "dpm_2",
            "dpm_2_ancestral",
            "lms",
            "dpm_fast",
            "dpmpp_sde",
            "dpmpp_sde_gpu",
            "dpmpp_2m",
            "dpmpp_2m_sde",
            "dpmpp_2m_sde_gpu",
            "dpmpp_3m_sde",
            "dpmpp_3m_sde_gpu",
            "ddim",
            "ddpm",
            "lcm",
            "uni_pc",
            "uni_pc_bh2",
            "res_multistep",
            "res_multistep_ancestral",
            "ipndm",
            "ipndm_v",
            "deis",
            "gradient_estimation",
            "er_sde",
            "seeds_2",
            "seeds_3",
            "sa_solver",
            "sa_solver_pece",
            "euler_cfg_pp",
            "euler_ancestral_cfg_pp",
            "dpmpp_2m_cfg_pp",
            "dpmpp_2s_ancestral_cfg_pp",
            "res_multistep_cfg_pp",
            "res_multistep_ancestral_cfg_pp",
            "gradient_estimation_cfg_pp",
        ],
    },
    "tiling": {
        "type": bool,
        "maps_to": "tiling",
        "default_value": True,
    },
}
COMMAND_IMAGE_ALIAS: str = "/image"
COMMAND_ATTACH_ALIAS: str = "/attach"
COMMAND_HELP_ALIAS: str = "/help"
COMMAND_EXIT_ALIAS: str = "/exit"