import os
import base64
import re
import opengpt_constants

def new_print(string: str, string_color: str, end: str = "\n") -> None:
    print(f"{string_color}{string}{opengpt_constants.PRINT_COLORS["reset"]}", end=end)

def process_text(text: str, return_with_thoughts: bool) -> str:
    pattern_matches: list = re.findall(r"(<think>.*?</think>\n*)(.*?)(?=<think>|$)", text, re.DOTALL)

    if return_with_thoughts or len(pattern_matches) == 0:
        return text

    text_buffer: str = ""
    for pattern_match in pattern_matches:
        text_buffer += pattern_match[1]
    return text_buffer

def strip_leading_and_trailing_quotes(text: str) -> str:
    return text.removeprefix("\"").removesuffix("\"")

def get_file_extension(path: str, omit_dot: bool) -> str:
    file_extension: str = os.path.splitext(path)[1].lower()
    return file_extension if not omit_dot else file_extension[1:]

def is_generic_url(url: str) -> bool:
    for url_pattern in opengpt_constants.TEXT_MODEL_ATTACHMENT_GENERIC_URL_PATTERNS:
        if re.search(url_pattern, url):
            return True
    return False

def get_image_data(path: str) -> str:
    with open(path, "rb") as file:
        return f"data:image/{get_file_extension(path, True)};base64,{base64.b64encode(file.read()).decode()}"

def get_audio_data(path: str) -> dict:
    with open(path, "rb") as file:
        return {
            "data": base64.b64encode(file.read()).decode(),
            "format": get_file_extension(path, True)
        }

def construct_arguments(arguments: list[str]) -> str:
    argument_buffer: str = ""
    for argument in arguments:
        argument = argument.strip()
        if argument != "":
            argument_buffer += f"{argument} "
    return argument_buffer.rstrip()

def clamp_float(value: float, min_value: float, max_value: float) -> float:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value

def clamp_int(value: int, min_value: int, max_value: int) -> int:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value