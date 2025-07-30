from typing import Any
import opengpt_constants
import opengpt_utils
import os
import io
import base64
from PIL import Image
import re
import time
import requests


_image_model: Any = None

def get_llama_server_status(server_url: str) -> bool:
    """
    Check the status of a llama.cpp server.

    Args:
        server_url: The base URL of the llama.cpp server.

    Returns:
        True if the server is running (HTTP 200), False otherwise.
    """

    return requests.get(f"{server_url}/health").status_code == 200

def get_llama_server_info(server_url: str) -> tuple[str, dict[str, Any]]:
    """
    Retrieve model ID and multimodal capabilities from a llama.cpp server.

    Args:
        server_url: The base URL of the llama.cpp server.

    Returns:
        Model ID and modalities dictionary.
    """

    model_id: str = opengpt_utils.get_filename_without_extension(requests.get(f"{server_url}/v1/models").json()["models"][0]["name"])
    model_modalities: dict[str, Any] = requests.get(f"{server_url}/props").json()["modalities"]
    return model_id, model_modalities

def generate_image(api_type: str, server_url: str, gen_params_match: re.Match[str]) -> tuple[dict[str, str] | str, float]:
    """
    Generate an image using the specified API.

    Args:
        api_type: The API used to generate images. Can be "internal", "sd_webui", "swarmui", or "koboldcpp".
        server_url: The base URL of the API server.
        gen_params_match: The RegEx match that contains image generation parameters.

    Returns:
        A tuple containing the image data (or error message if the process failed) and image generation time.
    """

    payload: dict[str, Any] = opengpt_utils.parse_params_regex_match(opengpt_constants.IMAGE_MODEL_GEN_PARAMS_SCHEMA, gen_params_match, api_type)
    start_time: float = time.time()

    calculate_gen_time = lambda: time.time() - start_time

    match api_type:
        case "internal":
            try:
                from stable_diffusion_cpp import StableDiffusion # type: ignore

                global _image_model

                if payload["unload_model"] and _image_model is not None:
                    _image_model = None
                    opengpt_utils.new_print("Unloaded image model", opengpt_constants.PRINT_COLORS["success"])

                if _image_model is None:
                    pattern: str = opengpt_utils.build_params_regex_pattern(opengpt_constants.IMAGE_MODEL_INTERNAL_INIT_PARAMS_SCHEMA, "", "")

                    match: re.Match[str] | None = re.match(pattern, input("No image model is loaded. Provide initialization parameters: ").strip())
                    if match is not None:
                        try:
                            init_params: dict[str, Any] = opengpt_utils.parse_params_regex_match(opengpt_constants.IMAGE_MODEL_INTERNAL_INIT_PARAMS_SCHEMA, match, "")

                            if not os.path.exists(init_params["model_path"]) or opengpt_utils.get_file_extension(init_params["model_path"]) not in [".safetensors", ".gguf"]:
                                return "File does not exist nor is a recognized image model", 0.0

                            match init_params["model_type"]:
                                case "sd":
                                    pass
                                case "flux":
                                    init_params["diffusion_model_path"] = init_params["model_path"]
                                    init_params.pop("model_path")
                                case _:
                                    return "Unknown image model type", 0.0
                            init_params.pop("model_type")
                            init_params["verbose"] = False

                            opengpt_utils.new_print("Loading image model", opengpt_constants.PRINT_COLORS["success"])
                            _image_model = StableDiffusion(**init_params)
                            start_time = time.time()
                        except ValueError:
                            return "Failed to load image model", 0.0
                    else:
                        return "Error", 0.0

                payload.pop("unload_model")
                payload["seed"] = -1

                opengpt_utils.new_print("Generating...", opengpt_constants.PRINT_COLORS["success"])
                image: Image.Image = _image_model.txt_to_img(**payload)[0]
                image_buffer: io.BytesIO = io.BytesIO()
                image.save(image_buffer, "png")
                image_base64: str = base64.b64encode(image_buffer.getvalue()).decode()
                return _build_image_data(image_base64, payload["prompt"], payload["negative_prompt"]), calculate_gen_time()
            except ImportError:
                return "OpenGPT-CLI - Python module 'stable-diffusion-cpp-python' is required for this API", 0.0
        case "sd_webui" | "koboldcpp":
            try:
                loaded_model_ids: list[dict[str, Any]] = requests.get(f"{server_url}/sdapi/v1/sd-models").json()
                if len(loaded_model_ids) > 0:
                    try:
                        if api_type == "sd_webui":
                            # Here, we attempt to generate a throwaway image. If the JSON has the images dictionary, it means
                            # the API is enabled.
                            dummy_payload: dict[str, Any] = {
                                "prompt": "cat",
                                "width": 64,
                                "height": 64,
                                "steps": 1,
                                "sampler_name": "DPM++ 2M",
                                "scheduler": "Automatic",
                            }
                            if "images" not in requests.post(f"{server_url}/sdapi/v1/txt2img", json=dummy_payload).json():
                                return "Stable Diffusion Web UI - API is disabled", 0.0

                            # This is not in KoboldCpp's SD Web UI API implementation.
                            payload["scheduler"] = "Automatic"

                        payload["sampler_name"] = "Euler a"

                        opengpt_utils.new_print("Generating...", opengpt_constants.PRINT_COLORS["success"])
                        image_base64: str = requests.post(f"{server_url}/sdapi/v1/txt2img", json=payload).json()["images"][0]
                        return _build_image_data(image_base64, payload["prompt"], payload["negative_prompt"]), calculate_gen_time()
                    except requests.exceptions.ConnectionError:
                        return "Stable Diffusion Web UI - An error occurred", 0.0
                else:
                    return "Stable Diffusion Web UI - No image models loaded", 0.0
            except requests.exceptions.ConnectionError:
                return "Stable Diffusion Web UI - Failed to retrieve model list. Is it running?", 0.0
        case "swarmui":
            try:
                # This is so API calls can be made to SwarmUI.
                headers = {
                    "Content-Type": "application/json",
                }

                session_id: str = requests.post(f"{server_url}/API/GetNewSession", json={}, headers=headers).json()["session_id"] # Needed for making requests to the API.
                model_ids: list[str] = []
                model_id: str = ""

                for model_info in requests.post(f"{server_url}/API/ListLoadedModels", json={"session_id": session_id}, headers=headers).json()["models"]:
                    model_ids.append(opengpt_utils.get_filename_without_extension(model_info["name"]))

                if len(model_ids) == 0:
                    return "SwarmUI - No image models loaded", 0.0
                elif len(model_ids) == 1:
                    model_id = model_ids[0]
                elif len(model_ids) >= 2:
                    try:
                        chosen_model_id_index: int = int(input(f"Multiple image models are available, choose one (1-{len(model_ids)}): "))

                        # noinspection PyChainedComparisons
                        if chosen_model_id_index >= 1 and chosen_model_id_index <= len(model_ids):
                            model_id = model_ids[chosen_model_id_index - 1]
                        else:
                            model_id = model_ids[0]
                            opengpt_utils.new_print("Got invalid index, defaulting to 1", opengpt_constants.PRINT_COLORS["warning"])
                    except ValueError:
                        model_id = model_ids[0]
                        opengpt_utils.new_print("Error while converting input to int, defaulting to 1", opengpt_constants.PRINT_COLORS["warning"])

                try:
                    payload["session_id"] = session_id
                    payload["model"] = model_id
                    payload["images"] = 1
                    payload["donotsave"] = True
                    payload["seed"] = -1

                    opengpt_utils.new_print("Generating...", opengpt_constants.PRINT_COLORS["success"])
                    image_base64: str = requests.post(f"{server_url}/API/GenerateText2Image", json=payload).json()["images"][0]
                    return _build_image_data(image_base64, payload["prompt"], payload["negativeprompt"]), calculate_gen_time()
                except requests.exceptions.ConnectionError:
                    return "SwarmUI - An error occurred", 0.0
            except requests.exceptions.ConnectionError:
                return "SwarmUI - Failed to retrieve model list. Is it running?", 0.0
        case "fooocus":
            return "Fooocus - API is unimplemented", 0.0
        case _:
            return "Unknown API type", 0.0

def _build_image_data(image_base64: str, positive_prompt: str, negative_prompt: str) -> dict[str, str]:
    if not image_base64.startswith("data:image/png;base64,"):
        image_base64 = f"data:image/png;base64,{image_base64}"
    return {
        "image": image_base64,
        "positive_prompt": positive_prompt,
        "negative_prompt": negative_prompt,
    }