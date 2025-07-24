This is a CLI for interacting with language models and image models. Currently, it only supports Windows.

The `text_models` and `image_models` folders are only for organization, the CLI can load a model from anywhere in the file system.

# Installation

- Install **[Python 3.13](https://www.python.org/downloads/)**
- Download **[llama.cpp](https://github.com/ggml-org/llama.cpp/releases/latest)**
- Optionally, to use image generation, download **[KoboldCpp](https://github.com/LostRuins/koboldcpp/releases/latest)** (if using AMD, get it from [here](https://github.com/YellowRoseCx/koboldcpp-rocm))

# Language Models

When in doubt which `.gguf` to download, take your GPU's VRAM and use the file size as a guideline. It's recommended to have a minimum of **16GB RAM** and **6GB VRAM**.

A model is considered multimodal if it follows this file structure:

```
# Example for Pixtral 12B
pixtral-12b.gguf
pixtral-12b-mmproj.gguf

# Example for Qwen2-Audio 7B
qwen2-audio-7b.gguf
qwen2-audio-7b-mmproj.gguf
```

Thus, if you download a multimodal projector for a model, you may need to rename it.

## Text-Only Models

- **[Qwen3 0.6B](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/main)**
    - Good for potato PCs.
- **[Qwen3 1.7B](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main)**
- **[Qwen3 4B](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/main)**
- **[Qwen3 8B](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/main)**
- **[Gemma 3 1B](https://huggingface.co/unsloth/gemma-3-1b-it-GGUF/tree/main)**
    - Good for potato PCs.

## Multimodal Models

- **[Qwen2-Audio 7B](https://huggingface.co/mradermacher/Qwen2-Audio-7B-Instruct-GGUF/tree/main)**
    - Make sure to download both the model and multimodal projector (f16/Q8_0).
- **[Gemma 3 4B](https://huggingface.co/unsloth/gemma-3-4b-it-qat-GGUF/tree/main)**
    - Make sure to download the multimodal projector (f32/f16/bf16).
- **[Tiger Gemma 12B v3](https://huggingface.co/TheDrummer/Tiger-Gemma-12B-v3-GGUF/tree/main)**
    - Less censored version of **Gemma 3 12B**.
    - Get the multimodal projector from [here](https://huggingface.co/koboldcpp/mmproj/resolve/main/gemma3-12b-mmproj.gguf?download=true).

# Image Models

**Stable Diffusion (1.5, XL)** models will be primarily talked about here; they are often provided as `.safetensors` files, which take up a lot of memory when loaded. If you want to run one alongside the LM and your hardware isn't powerful enough, you may need to quantize the image model.

To quantize image models, you'll need **[stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp/releases/latest)**. Alternatively, you can get a pre-quantized image model from [here](https://huggingface.co/koboldcpp/imgmodel/tree/main).

# Documentation

## Chat Mode Commands

- `/image`: Generate an image (requires the image model server to be online).
- `/attach`: Attach a file or image URL to your message (command must be at the end of your message).
- `/help`: Show all commands.
- `/exit`: Exit the application.

## Supported Attachments

- **Generic:** Refer to `TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES` and `TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS` in `app.py` (too many to list here).
- **Images:** `JPEG, JPEG XL, JPEG LS, JPEG XR, PNG, TIFF, WebP`
- **Audio:** `WAV, MP3`