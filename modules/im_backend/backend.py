from modules import global_vars
from .interfaces import ImageModelInterface, SDCppInterface, KoboldCppInterface, SDWebUIInterface, SwarmUIInterface

def init_interface(interface: str) -> None:
    if type(global_vars.image_model_interface) == ImageModelInterface:
        match interface:
            case "internal":
                global_vars.image_model_interface = SDCppInterface("", "", "prompt", "negative_prompt")
            case "koboldcpp":
                global_vars.image_model_interface = KoboldCppInterface("http://localhost:5001", "/sdapi/v1/txt2img", "prompt", "negative_prompt")
            case "sd_webui":
                global_vars.image_model_interface = SDWebUIInterface("http://localhost:7860", "/sdapi/v1/txt2img", "prompt", "negative_prompt")
            case "swarmui":
                global_vars.image_model_interface = SwarmUIInterface("http://localhost:7801", "/API/GenerateText2Image", "prompt", "negativeprompt")
            case _:
                raise ValueError
