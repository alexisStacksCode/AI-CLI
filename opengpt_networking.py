from typing import Any
import time
import requests
import opengpt_constants
import opengpt_utils


def get_llama_server_status(server_url: str) -> bool:
    """
    Check the status of a llama.cpp server.

    Args:
        server_url: The base URL of the llama.cpp server.

    Returns:
        True if the server is running (HTTP 200), False otherwise.
    """

    return requests.get(f"{server_url}/health").status_code == 200


def get_llama_server_info(server_url: str) -> tuple[str, dict[str, bool]]:
    """
    Retrieve model ID and multimodal capabilities from a llama.cpp server.

    Args:
        server_url: The base URL of the llama.cpp server.

    Returns:
        Model ID and modalities dictionary.
    """

    model_id: str = opengpt_utils.get_filename_without_extension(requests.get(f"{server_url}/v1/models").json()["models"][0]["name"])
    model_modalities: dict[str, bool] = requests.get(f"{server_url}/props").json()["modalities"]
    return model_id, model_modalities


def generate_image(api_type: str, server_url: str, gen_params: dict[str, Any]) -> tuple[dict[str, Any] | str, float]:
    """
    Generate an image using the specified API.

    Args:
        api_type: The API used to generate images. Can be "sd_webui", "swarmui", or "koboldcpp".
        server_url: The base URL of the API server.
        gen_params: Image generation parameters.

    Returns:
        A tuple containing the image data (or error message if the process failed) and image generation time.
    """

    # TODO: reimplement value validation
    for gen_param_info in opengpt_constants.IMAGE_MODEL_AVAILABLE_GEN_PARAMS.values():
        real_name: str | None = gen_param_info["maps_to"][api_type]
        if real_name is None:
            continue

        if gen_params[real_name] is None and "default_value" in gen_param_info:
            gen_params[real_name] = gen_param_info["default_value"]

        if type(gen_params[real_name]) == str:
            if gen_param_info["type"] == bool:
                match gen_params[real_name]:
                    case "true":
                        gen_params[real_name] = True
                    case "false":
                        gen_params[real_name] = False
                    case _:
                        gen_params[real_name] = True if "default_value" not in gen_param_info else \
                        gen_param_info["default_value"]
            elif gen_param_info["type"] == float:
                gen_params[real_name] = float(gen_params[real_name])
            elif gen_param_info["type"] == int:
                gen_params[real_name] = int(gen_params[real_name])

    payload: dict[str, Any] = gen_params.copy()
    start_time: float = time.time()

    calculate_gen_time = lambda: time.time() - start_time

    match api_type:
        case "sd_webui" | "koboldcpp":
            try:
                loaded_model_ids: list[dict[str, Any]] = requests.get(f"{server_url}/sdapi/v1/sd-models").json()
                if len(loaded_model_ids) > 0:
                    try:
                        # here, we attempt to generate a throwaway image. if the JSON has the images dictionary, it means
                        # the API is enabled. if KoboldCpp (which implements SD WebUI-compatible API) is used, there's
                        # no need to check API availability.
                        if api_type == "sd_webui":
                            dummy_payload: dict[str, Any] = {
                                "prompt": "cat",
                                "width": 64,
                                "height": 64,
                                "steps": 1,
                                "sampler_name": "DPM++ 2M",
                                "scheduler": "Automatic",
                            }
                            if "images" not in requests.post(f"{server_url}/sdapi/v1/txt2img", json=dummy_payload).json():
                                return "Stable Diffusion WebUI - API is disabled", 0.0

                            payload["scheduler"] = "Automatic"

                        payload["sampler_name"] = "Euler a"

                        opengpt_utils.new_print("Generating...", opengpt_constants.PRINT_COLORS["success"])
                        image_base64: str = requests.post(f"{server_url}/sdapi/v1/txt2img", json=payload).json()["images"][0]
                        return _build_image_data(image_base64, payload["prompt"], payload["negative_prompt"]), calculate_gen_time()
                    except requests.exceptions.ConnectionError:
                        return "Stable Diffusion WebUI - An error occurred", 0.0
                else:
                    return "Stable Diffusion WebUI - No image models loaded", 0.0
            except requests.exceptions.ConnectionError:
                return "Stable Diffusion WebUI - Failed to retrieve model list. Is it running?", 0.0
        case "swarmui":
            try:
                # this is so API calls can be made to SwarmUI
                headers = {
                    "Content-Type": "application/json",
                }

                session_id: str = requests.post(f"{server_url}/API/GetNewSession", json={}, headers=headers).json()["session_id"]  # needed for making requests to the API
                model_ids: list[str] = []
                model_id: str = ""

                for model_info in requests.post(f"{server_url}/API/ListLoadedModels", json={"session_id": session_id}, headers=headers).json()["models"]:
                    model_ids.append(opengpt_utils.get_filename_without_extension(model_info["name"]))

                if len(model_ids) == 0:
                    return "SwarmUI - No image models loaded", 0.0
                elif len(model_ids) == 1:
                    model_id = model_ids[0]
                elif len(model_ids) >= 2:
                    # TODO: present the user with an option to select an image model
                    return "TODO", 0.0

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