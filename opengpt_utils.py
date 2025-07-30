from typing import Any
from opengpt_types import ParamsSchema
import opengpt_constants
from opengpt_gguf import GGUFParser
import os
import re

def new_print(text: str, color: str, end: str = "\n") -> None:
    """
    Print text with the given color.

    Args:
        text: The text to print.
        color: The ANSI color code to apply.
        end: The string to append to `text`.
    """

    print(colorize_text(text, color), end=end)

def colorize_text(text: str, color: str) -> str:
    """
    Apply ANSI color formatting to text.

    Args:
        text: The text to colorize.
        color: The ANSI color code to apply.

    Returns:
        The colorized text string with reset code appended.
    """

    return f"{color}{text}{opengpt_constants.PRINT_COLORS["reset"]}"

def is_valid_text_model(path: str) -> bool:
    if not os.path.exists(path) or get_file_extension(path) != ".gguf":
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

def calculate_gpu_layers_for_text_model(path: str, mmproj_path: str) -> int:  # TODO: implement algorithm
    return 0

def build_params_regex_pattern(params_schema: ParamsSchema, leading_text: str, kind: str) -> str:
    """
    Args:
        params_schema:
        leading_text:
        kind:

    Returns:
        A string.
    """

    pattern: str = rf"^{leading_text}"
    for param_name, param_info in params_schema.items():
        real_name: str | None = param_info["maps_to"] if kind == "" else param_info["maps_to"][kind]
        if real_name is None:
            continue

        param_pattern: str = rf"\s+(?:{param_name}=)?"
        if param_info["type"] == str:
            param_pattern += rf"\"(?P<{real_name}>[^\"]+)\""
        elif param_info["type"] == bool:
            param_pattern += rf"(?P<{real_name}>true|false)"
        elif param_info["type"] == float:
            param_pattern += rf"(?P<{real_name}>\d+\.\d+)"
        elif param_info["type"] == int:
            param_pattern += rf"(?P<{real_name}>\d+)"

        if "default_value" in param_info:
            param_pattern = rf"(?:{param_pattern})?"

        pattern += param_pattern
    pattern += r"$"
    if leading_text == "":
        pattern = pattern.replace(r"^\s+", r"^") # if leading_text is empty, remove the space before the first parameter.
    return pattern


def parse_params_regex_match(params_schema: ParamsSchema, match: re.Match[str], kind: str) -> dict[str, Any]:
    """
    Args:
        params_schema: 
        match: 
        kind: 

    Returns:
        A dictionary.
    """

    provided_params: dict[str, Any] = match.groupdict()
    for param_info in params_schema.values():
        real_name: str | None = param_info["maps_to"] if kind == "" else param_info["maps_to"][kind]
        if real_name is None:
            continue

        if provided_params[real_name] is None and "default_value" in param_info:
            provided_params[real_name] = param_info["default_value"]

        if type(provided_params[real_name]) == str:
            if param_info["type"] == bool:
                match provided_params[real_name]:
                    case "true":
                        provided_params[real_name] = True
                    case "false":
                        provided_params[real_name] = False
                    case _:
                        provided_params[real_name] = True if "default_value" not in param_info else param_info["default_value"]
            elif param_info["type"] == float:
                provided_params[real_name] = float(provided_params[real_name])
            elif param_info["type"] == int:
                provided_params[real_name] = int(provided_params[real_name])
    return provided_params


def get_file_extension(file_path: str, omit_dot: bool = False) -> str:
    """
    Extract the file extension from a file path.

    Args:
        file_path: The path to extract the extension from.
        omit_dot: If True, returns the extension without the leading dot.

    Returns:
        The file extension, with or without the leading dot based on `omit_dot`.
    """

    file_extension: str = os.path.splitext(file_path)[1]
    return file_extension if not omit_dot else file_extension[1:]


def get_filename_without_extension(file_path: str) -> str:
    """
    Extract the filename without extension from a file path.

    Args:
        file_path: The full path.

    Returns:
        The filename without its extension.
    """

    return os.path.splitext(os.path.basename(file_path))[0]


def strip_path_quotes(file_path: str) -> str:
    """
    Remove surrounding quotes from a file path string.

    Args:
        file_path: The path that may have surrounding quotes.

    Returns:
        The path with leading and trailing quotes removed.
    """

    return file_path.removeprefix("\"").removesuffix("\"")


def build_arguments(arguments: list[str]) -> str:
    """
    Build a space-separated argument string from a list of arguments.

    Strips whitespace from each argument and joins non-empty arguments
    with spaces.

    Args:
        arguments: List of argument strings to process.

    Returns:
        A single string with arguments joined by spaces.
    """

    arguments_string: str = ""
    for index in range(len(arguments)):
        arguments[index] = arguments[index].strip()
        if arguments[index] != "":
            arguments_string += f"{arguments[index]}{" " if index != len(arguments) - 1 else ""}"
    return arguments_string


def clamp_float(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a float value to be within the specified range.

    Args:
        value: The value to clamp.
        min_value: The minimum allowed value.
        max_value: The maximum allowed value.

    Returns:
        The clamped value, guaranteed to be between `min_value` and `max_value`.
    """

    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value


def clamp_int(value: int, min_value: int, max_value: int) -> int:
    """
    Clamp an integer value to be within the specified range.

    Args:
        value: The value to clamp.
        min_value: The minimum allowed value.
        max_value: The maximum allowed value.

    Returns:
        The clamped value, guaranteed to be between `min_value` and `max_value`.
    """

    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value