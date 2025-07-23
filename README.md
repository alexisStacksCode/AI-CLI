This is a CLI for interacting with language models and image models. To get started, refer to **Installation**.

# Installation

- Get **Python 3.13** from: https://www.python.org/downloads/
- Get **llama.cpp** from: https://github.com/ggml-org/llama.cpp/releases/latest
- *(Optional, required for image generation)* Get **KoboldCpp** from: https://github.com/LostRuins/koboldcpp/releases/latest

# Language Models

When in doubt which `.gguf` to download, take your GPU's VRAM and use the file size as a guideline. It's recommended to have a minimum of **16GB RAM** and **6GB VRAM**.

## Text-Only Models

- [Qwen3 0.6B](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/main)
    - Good for potato PCs.
- [Qwen3 1.7B](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main)
- [Qwen3 4B](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/main)
- [Qwen3 8B](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/main)
- [Gemma 3 1B](https://huggingface.co/unsloth/gemma-3-1b-it-GGUF/tree/main)
    - Good for potato PCs.

## Multimodal Models

- [Qwen2-Audio 7B](https://huggingface.co/mradermacher/Qwen2-Audio-7B-Instruct-GGUF/tree/main)
    - Make sure to download both the model and multimodal projector (f16/Q8_0).
- [Gemma 3 4B](https://huggingface.co/unsloth/gemma-3-4b-it-qat-GGUF/tree/main)
    - Get the multimodal projector from: https://huggingface.co/koboldcpp/mmproj/tree/main
- [Tiger Gemma 12B v3](https://huggingface.co/TheDrummer/Tiger-Gemma-12B-v3-GGUF/tree/main)
    - Less censored version of **Gemma 3 12B**.
    - Get the multimodal projector from: https://huggingface.co/koboldcpp/mmproj/tree/main

# Image Models

**Stable Diffusion (1.5, XL)** models will be covered here. They are often provided as `.safetensors` files, which take up a lot of memory when loaded.

You need **[stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp/releases/latest)** in order to quantize image models. Alternatively, you can get a pre-quantized image model from: https://huggingface.co/koboldcpp/imgmodel/tree/main

# Commands

- `/image`: Generate an image (requires the image model server to be online).
- `/attach`: Attach a file or image URL to your message (command must be at the end of your message).
- `/help`: Show all commands.
- `/exit`: Exit the application.