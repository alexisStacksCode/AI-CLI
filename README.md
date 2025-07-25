# OpenGPT-CLI

**OpenGPT-CLI** is a console application that utilizes **llama.cpp** for language model inference and **KoboldCpp** for image model inference; these two applications aren't integrated into **OpenGPT-CLI** but rather, it interfaces with them. Its key features are two modes (Chat Mode, Autocomplete Mode), the ability to attach files/URLs to your messages in Chat Mode, and comprehensive settings.

It's recommended that your hardware has a minimum of **16GB RAM** and **6GB VRAM** for the best performance.

Windows is primarily supported, other platforms have not been tested.

## Get Started

Getting started with **OpenGPT-CLI** is straightforward. You can either:

- [Download the latest release](https://github.com/alexisStacksCode/OpenGPT-CLI/releases/latest)
- Clone the repository

Once you have extracted the folder, you'll need to do the following:

- [Get **Python** (`>=3.13` recommended)](https://www.python.org/downloads/)
- [Download **llama.cpp**](https://github.com/ggml-org/llama.cpp/releases/latest)
- If you want image generation capabilities, [download **KoboldCpp**](https://github.com/LostRuins/koboldcpp/releases/latest)

Finally, open the folder in **Terminal** and run `pip install -r requirements.txt`. After that, you can run **OpenGPT-CLI** with `run.bat`.

## Language Models

**llama.cpp** uses `.gguf` models. You can get them from [**Hugging Face**](https://huggingface.co/models?library=gguf&sort=trending); recommended sources are [mradermacher](https://huggingface.co/mradermacher) and [bartowski](https://huggingface.co/bartowski).

Multimodal LM support (vision, audio) is implemented. However, the application considers a text model to be multimodal only if it detects a `text_model-mmproj.gguf` file in the same directory as `text_model.gguf`.

```
# Example for Pixtral 12B
C:/models/Pixtral-12B-Q4_K_M.gguf
C:/models/Pixtral-12B-Q4_K_M-mmproj.gguf

# Example for Qwen2-Audio 7B
C:/models/Qwen2-Audio-7B-IQ4_XS.gguf
C:/models/Qwen2-Audio-7B-IQ4_XS-mmproj.gguf
```

Thus, if you download a multimodal projector for a text model, you may need to rename it.

## Image Models

**KoboldCpp** uses both `.safetensors` and `.gguf` models. You can get them from [**Civitai**](https://civitai.com/) and [**Tensor.Art**](https://tensor.art/). It's recommended to get started with this [**Hugging Face** repository](https://huggingface.co/koboldcpp/imgmodel/tree/main) for pre-quantized image models.

To quantize image models, you'll need [**stable-diffusion.cpp**](https://github.com/leejet/stable-diffusion.cpp/releases/latest). Image models quantized with other methods may fail to load.

## Documentation

Documentation is available at https://github.com/alexisStacksCode/OpenGPT-CLI/wiki.