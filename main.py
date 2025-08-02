import argparse
from modules import global_vars, modes, lm_backend
from modules.core import launch_args

if __name__ == "__main__":
    arguments: argparse.Namespace = launch_args.get()

    lm_backend.init_interface(arguments.lm_backend if arguments.lm_backend is not None else "internal")
    global_vars.text_model_interface.launch(arguments.model if arguments.model is not None else "")

    #im_backend.init_interface("internal")

    modes.loop(arguments.mode if arguments.mode is not None else "chat")
