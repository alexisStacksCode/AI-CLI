from typing import Any
import os
import re


def build_params_regex(param_schema: dict[str, dict[str, Any]], leading_text: str, kind: str) -> str:
    pattern: str = rf"^{leading_text}"
    for param_name, param_info in param_schema.items():
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
        pattern = pattern.replace(r"^\s+", r"^")  # If leading_text is empty, remove the space before the first parameter.
    return pattern


def parse_params_regex(param_schema: dict[str, dict[str, Any]], regex_match: re.Match[str], kind: str) -> dict[str, Any]:
    extracted_params: dict[str, Any] = regex_match.groupdict()
    for param_info in param_schema.values():
        real_name: str | None = param_info["maps_to"] if kind == "" else param_info["maps_to"][kind]
        if real_name is None:
            continue

        if extracted_params[real_name] is None and "default_value" in param_info:
            extracted_params[real_name] = param_info["default_value"]

        if type(extracted_params[real_name]) == str:
            if param_info["type"] == bool:
                match extracted_params[real_name]:
                    case "true":
                        extracted_params[real_name] = True
                    case "false":
                        extracted_params[real_name] = False
                    case _:
                        extracted_params[real_name] = True if "default_value" not in param_info else param_info[
                            "default_value"]
            elif param_info["type"] == float:
                extracted_params[real_name] = float(extracted_params[real_name])
            elif param_info["type"] == int:
                extracted_params[real_name] = int(extracted_params[real_name])
    return extracted_params


def build_argument_string(arguments: list[str]) -> str:
    argument_string: str = ""
    for index in range(len(arguments)):
        arguments[index] = arguments[index].strip()
        if arguments[index] != "":
            argument_string += f"{arguments[index]}{" " if index != len(arguments) - 1 else ""}"
    return argument_string


def get_file_extension(file_path: str, omit_dot: bool = False) -> str:
    file_extension: str = os.path.splitext(file_path)[1]
    return file_extension if not omit_dot else file_extension[1:]


def get_filename_without_extension(file_path: str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]


def strip_path_quotes(file_path: str) -> str:
    return file_path.removeprefix("\"").removesuffix("\"")
