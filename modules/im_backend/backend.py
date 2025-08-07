from .interfaces import ImageModelInterface, SDCppInterface, KoboldCppInterface, SDWebUIInterface, SwarmUIInterface


interface: ImageModelInterface | None = None


def init_interface(interface_name: str) -> None:
    global interface

    if interface is None:
        match interface_name:
            case "internal":
                interface = SDCppInterface("", "", "prompt", "negative_prompt")
            case "koboldcpp":
                interface = KoboldCppInterface("http://localhost:5001", "/sdapi/v1/txt2img", "prompt", "negative_prompt")
            case "sd_webui":
                interface = SDWebUIInterface("http://localhost:7860", "/sdapi/v1/txt2img", "prompt", "negative_prompt")
            case "swarmui":
                interface = SwarmUIInterface("http://localhost:7801", "/API/GenerateText2Image", "prompt", "negativeprompt")
            case _:
                raise ValueError
