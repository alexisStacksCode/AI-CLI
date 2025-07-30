# OpenGPT-CLI

OpenGPT-CLI is a console application that utilizes **llama.cpp** for language model inference. It can also interface with various AI image generation software like **Stable Diffusion Web UI** and **SwarmUI**, or perform image model inference directly through the **stable-diffusion-cpp-python** library.

The current version is `2.0.0-dev`. The previous version was `1.1.1`.

## Codebase

* `opengpt.py`: Main application code.
* `opengpt_types.py`: Type definitions.
* `opengpt_constants.py`: Enums and constants.
* `opengpt_utils.py`: Utility functions.
* `opengpt_networking.py`: API-related functions.
* `opengpt_gguf.py`: Implements the `GGUFParser` class, which is used to read `.gguf` files.