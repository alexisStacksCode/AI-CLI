from typing import Any
import os
import io
import base64
import re
import time

import requests

from modules.core.types import ImageGenResult
from modules.core.enums import PrintColors
from modules.core import constants
from modules import utils


# TODO: update this
class ImageModelInterface:
    def __init__(self, api_url: str, api_endpoint: str, positive_prompt_key: str, negative_prompt_key: str) -> None:
        self._api_url: str = api_url
        self._api_endpoint: str = api_endpoint
        self._gen_start_time: float = 0.0
        self._positive_prompt_key: str = positive_prompt_key
        self._negative_prompt_key: str = negative_prompt_key

    def call(self, payload: dict[str, Any]) -> ImageGenResult:
        raise NotImplementedError

    def _post_init(self, payload: dict[str, Any]) -> None:
        pass

    def _pre_generate(self) -> None:
        self._gen_start_time = time.time()
        utils.terminal.new_print("Generating...", PrintColors.SUCCESS)

    def _generate(self, payload: dict[str, Any]) -> ImageGenResult:
        self._pre_generate()
        image_base64: str = requests.post(f"{self._api_url}{self._api_endpoint}", json=payload).json()["images"][0]
        return self._build_image_data(image_base64), self._calculate_gen_time()

    def _build_image_data(self, image_base64: str) -> dict[str, str]:
        if not image_base64.startswith("data:image/png;base64,"):
            image_base64 = f"data:image/png;base64,{image_base64}"
        return {
            "image": image_base64,
            "positive_prompt": self._positive_prompt_key,
            "negative_prompt": self._negative_prompt_key,
        }

    def _calculate_gen_time(self) -> float:
        return time.time() - self._gen_start_time


class SDCppInterface(ImageModelInterface):
    _model: Any = None

    def call(self, payload: dict[str, Any]) -> ImageGenResult:
        try:
            import stable_diffusion_cpp  # pyright: ignore[reportMissingImports, reportUnusedImport, reportMissingTypeStubs]

            payload.pop("unload_model")
            payload["seed"] = -1
            return self._generate(payload)
        except ImportError:
            raise requests.exceptions.ConnectionError

    def _post_init(self, payload: dict[str, Any]) -> None:
        try:
            from stable_diffusion_cpp import StableDiffusion # pyright: ignore[reportUnknownVariableType, reportMissingImports, reportMissingTypeStubs]

            if payload["unload_model"] and SDCppInterface._model:
                SDCppInterface._model = None
                utils.terminal.new_print("Unloaded image model", PrintColors.SUCCESS)

            if SDCppInterface._model is None:
                pattern: str = utils.helpers.build_params_regex(constants.IMAGE_MODEL_INTERNAL_INIT_PARAMS_SCHEMA, "", "")

                match: re.Match[str] | None = re.match(pattern, input("No image model is loaded. Provide initialization parameters: ").strip())
                if match is not None:
                    init_params: dict[str, Any] = utils.helpers.parse_params_regex(constants.IMAGE_MODEL_INTERNAL_INIT_PARAMS_SCHEMA, match, "")

                    if not os.path.exists(init_params["model_path"]) or utils.helpers.get_file_extension(init_params["model_path"]) not in [".safetensors", ".gguf"]:
                        raise ValueError

                    match init_params["model_type"]:
                        case "sd":
                            pass
                        case "flux":
                            init_params["diffusion_model_path"] = init_params["model_path"]
                            init_params.pop("model_path")
                        case _:
                            raise ValueError
                    init_params.pop("model_type")
                    init_params["verbose"] = False

                    utils.terminal.new_print("Loading image model", PrintColors.SUCCESS)
                    SDCppInterface._model = StableDiffusion(**init_params)
                else:
                    raise ValueError
        except ImportError:
            raise requests.exceptions.ConnectionError

    def _generate(self, payload: dict[str, Any]) -> ImageGenResult:
        try:
            from PIL import Image  # pyright: ignore[reportUnknownVariableType, reportMissingImports]
            import stable_diffusion_cpp  # pyright: ignore[reportMissingImports, reportUnusedImport, reportMissingTypeStubs]

            self._pre_generate()
            image: Image.Image = SDCppInterface._model.txt_to_img(**payload)[0]  # pyright: ignore[reportUnknownMemberType]
            image_buffer: io.BytesIO = io.BytesIO()
            image.save(image_buffer, "png")  # pyright: ignore[reportUnknownMemberType]
            image_base64: str = base64.b64encode(image_buffer.getvalue()).decode()
            return self._build_image_data(image_base64), self._calculate_gen_time()
        except ImportError:
            raise requests.exceptions.ConnectionError


class KoboldCppInterface(ImageModelInterface):
    def call(self, payload: dict[str, Any]) -> ImageGenResult:
        payload["sampler_name"] = "Euler a"
        return self._generate(payload)

    def _post_init(self, payload: dict[str, Any]) -> None:
        loaded_model_ids: list[dict[str, Any]] = requests.get(f"{self._api_url}/sdapi/v1/sd-models").json()
        if len(loaded_model_ids) == 0:
            raise requests.exceptions.ConnectionError


class SDWebUIInterface(KoboldCppInterface):
    def call(self, payload: dict[str, Any]) -> ImageGenResult:
        payload["sampler_name"] = "Euler a"
        return super().call(payload)

    def _post_init(self, payload: dict[str, Any]) -> None:
        super()._post_init(payload)

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
        if "images" not in requests.post(f"{self._api_url}{self._api_gen_endpoint}", json=dummy_payload).json():
            raise requests.exceptions.ConnectionError


class SwarmUIInterface(ImageModelInterface):
    _session_id: str = ""
    _model_id: str = ""

    def call(self, payload: dict[str, Any]) -> ImageGenResult:
        payload["session_id"] = SwarmUIInterface._session_id
        payload["model"] = SwarmUIInterface._model_id
        payload["images"] = 1
        payload["donotsave"] = True
        payload["seed"] = -1
        return self._generate(payload)

    def _post_init(self, payload: dict[str, Any]) -> None:
        # This is so API calls can be made to SwarmUI.
        headers = {
            "Content-Type": "application/json",
        }

        if SwarmUIInterface._session_id == "":
            SwarmUIInterface._session_id = requests.post(f"{self._api_url}/API/GetNewSession", json={}, headers=headers).json()["session_id"]  # Needed for making requests to the API.

        model_ids: list[str] = []
        for model_info in requests.post(f"{self._api_url}/API/ListLoadedModels", json={"session_id": SwarmUIInterface._session_id}, headers=headers).json()["models"]:
            model_ids.append(utils.get_filename_without_extension(model_info["name"]))

        if len(model_ids) == 0:
            raise requests.exceptions.ConnectionError
        elif len(model_ids) == 1:
            SwarmUIInterface._model_id = model_ids[0]
        elif len(model_ids) >= 2:
            try:
                chosen_model_id_index: int = int(input(f"Multiple image models are available. Choose one (1-{len(model_ids)}): "))

                # noinspection PyChainedComparisons
                if chosen_model_id_index >= 1 and chosen_model_id_index <= len(model_ids):
                    SwarmUIInterface._model_id = model_ids[chosen_model_id_index - 1]
                else:
                    SwarmUIInterface._model_id = model_ids[0]
                    utils.new_print("Got invalid index, defaulting to 1", constants.PRINT_COLORS["warning"])
            except ValueError:
                SwarmUIInterface._model_id = model_ids[0]
                utils.new_print("Error while converting input to int, defaulting to 1", constants.PRINT_COLORS["warning"])
