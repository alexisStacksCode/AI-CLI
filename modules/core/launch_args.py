import argparse

def get() -> argparse.Namespace:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    argument_parser.add_argument("--model")
    argument_parser.add_argument("--lm-backend", choices=["internal", "llama_server"])
    argument_parser.add_argument("--im-backend", choices=["internal", "koboldcpp", "sd_webui", "swarmui"])
    argument_parser.add_argument("--mode", choices=["chat", "autocomplete", "diffusion"])
    return argument_parser.parse_args()
