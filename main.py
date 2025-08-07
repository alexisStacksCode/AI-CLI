import argparse
import json

from modules.core.enums import PrintColors
from modules import utils, modes, lm_backend
from modules import shared
from modules.core import launch_args, settings

if __name__ == "__main__":
    arguments: argparse.Namespace = launch_args.get()

    try:
        settings.load()
    except json.JSONDecodeError:
        utils.terminal.new_print("Malformed settings file", PrintColors.WARNING)
    settings.save()

    lm_backend_interface: str = arguments.lm_backend if arguments.lm_backend is not None else settings.get("lm_backend/interface")

    lm_backend.init_interface(lm_backend_interface)
    shared.text_model_interface.setup(arguments.model if arguments.model is not None else "", **settings.get(f"lm_backend/init/{lm_backend_interface}"))  # pyright: ignore[reportOptionalMemberAccess]

    #im_backend.init_interface("internal")

    modes.MODES[arguments.mode if arguments.mode is not None else settings.get("mode")]()
