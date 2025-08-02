import argparse
import json

from modules.core.enums import PrintColors
from modules import utils, global_vars, modes, lm_backend
from modules.core import launch_args, settings

if __name__ == "__main__":
    arguments: argparse.Namespace = launch_args.get()

    try:
        settings.load()
    except json.JSONDecodeError:
        utils.terminal.new_print("Malformed settings file", PrintColors.WARNING)
    settings.save()

    lm_backend.init_interface(arguments.lm_backend if arguments.lm_backend is not None else "llama_server")
    global_vars.text_model_interface.launch(arguments.model if arguments.model is not None else "")

    #im_backend.init_interface("internal")

    modes.loop(arguments.mode if arguments.mode is not None else "chat")
