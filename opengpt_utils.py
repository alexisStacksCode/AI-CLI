import os
import opengpt_constants
from opengpt_gguf import GGUFParser

def new_print(text: str, color: str, end: str="\n") -> None:
    print(colorize_text(text, color), end=end)

def colorize_text(text: str, color: str) -> str:
    return f"{color}{text}{opengpt_constants.PRINT_COLORS["reset"]}"

def is_text_model_valid(path: str) -> bool:
    if not os.path.exists(path) or get_file_extension(path) != opengpt_constants.TEXT_MODEL_EXTENSION:
        return False

    try:
        parser: GGUFParser = GGUFParser(path)
        parser.parse()

        if len(parser.metadata) == 0:
            # maybe an image model quantized with stable-diffusion.cpp?
            recognized_tensors: list[str] = []
            for key in parser.tensors.keys():
                if key.startswith("model.diffusion_model"):
                    recognized_tensors.append(key)
            if len(recognized_tensors) > 0:
                return False
        elif len(parser.metadata) > 0:
            # is it an image model quantized with ComfyUI-GGUF's custom llama.cpp, or a multimodal projector?
            if parser.metadata["general.architecture"] in ["flux", "sd1", "sdxl", "sd3", "aura", "ltxv", "hyvid", "wan", "hidream", "cosmos", "clip"]:
                return False
        return True
    except:
        return False

def calculate_gpu_layers_for_text_model(path: str, mmproj_path: str) -> int: # TODO: implement algorithm
    return 0

def get_file_extension(path: str, omit_dot: bool = False) -> str:
    file_extension: str = os.path.splitext(path)[1]
    return file_extension if not omit_dot else file_extension[1:]

def strip_path_quotes(path: str) -> str:
    return path.removeprefix("\"").removesuffix("\"")

def build_arguments(arguments: list[str]) -> str:
    a: str = ""
    for argument in arguments:
        argument = argument.strip()
        if argument != "":
            a += f"{argument} "
    return a.rstrip()

def clamp_float(value: float, min_value: float, max_value: float) -> float:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value

def clamp_int(value: int, min_value: int, max_value: int) -> int:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value