from modules.core import settings
from .interfaces import ImageModelInterface, SDCppInterface, KoboldCppInterface, SDWebUIInterface, SwarmUIInterface


interface: ImageModelInterface | None = None


def init_interface(interface_name: str) -> None:
    global interface

    if interface is None:
        match interface_name:
            case "internal":
                interface = SDCppInterface("", "", "prompt", "negative_prompt")
            case "koboldcpp":
                interface = KoboldCppInterface(f"http://localhost:{__get_port(5001)}", "/sdapi/v1/txt2img", "prompt", "negative_prompt")
            case "sd_webui":
                interface = SDWebUIInterface(f"http://localhost:{__get_port(7860)}", "/sdapi/v1/txt2img", "prompt", "negative_prompt")
            case "swarmui":
                interface = SwarmUIInterface(f"http://localhost:{__get_port(7801)}", "/API/GenerateText2Image", "prompt", "negativeprompt")
            case _:
                raise ValueError


def __get_port(default_port: int) -> int:
    port: int = settings.get("im_backend/port")
    return port if port != -1 else default_port
