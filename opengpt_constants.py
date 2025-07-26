import colorama

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
    "reset": colorama.Style.RESET_ALL,
}
SERVER_FILENAMES: list[str] = [
    "koboldcpp.exe",
    "koboldcpp-nocuda.exe",
    "koboldcpp-oldpc.exe",
    "koboldcpp_cu12.exe",
    "koboldcpp_nocuda.exe",
    "koboldcpp_oldcpu.exe",
    "koboldcpp_rocm.exe",
    "koboldcpp_rocm_b2.exe",
    "koboldcpp.py",
]
SERVER_CHECK_INTERVAL: float = 1.0
MAX_SERVER_CHECKS: int = 20
SERVER_GPU_ACCELERATION_OPTIONS: list[str] = [
    "none",
    "cuda",
    "cuda_low_vram",
    "hip",
    "hip_low_vram",
    "vulkan",
    "opencl",
]
SERVER_LM_KV_CACHE_DATA_TYPES: dict[str, int] = {
    "f16": 0,
    "q8": 1,
    "q4": 2,
}
SERVER_LM_CONTEXT_PROCESSING_OPTIONS: list[str] = [
    "none",
    "context_shift",
    "smart_context",
]
TEXT_MODEL_EXTENSIONS: list[str] = [
    ".gguf",
    ".bin",
]
TEXT_MODEL_MIROSTAT_MODES: dict[str, int] = {
    "none": 0,
    "v1": 1,
    "v2": 2,
}
TEXT_MODEL_CHAT_SYSTEM_PROMPT_PATH: str = "chat_system_prompt.txt"
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
    ".flac",
]
IMAGE_MODEL_OUTPUT_DIR_NAME: str = "image_outputs/"
IMAGE_MODEL_EXTENSIONS: list[str] = [
    ".safetensors",
    ".gguf",
]
IMAGE_MODEL_EXCLUDED_PAYLOAD_KEYS: list[str] = [
    "open_image_on_gen",
]
COMMAND_IMAGE_ALIAS: str = "/image"
COMMAND_ATTACH_ALIAS: str = "/attach"
COMMAND_HELP_ALIAS: str = "/help"
COMMAND_EXIT_ALIAS: str = "/exit"