# Introduction

This is a CLI for interacting with language models and image models. Currently, Windows is supported; other platforms have not been tested.

The `text_models` and `image_models` folders are only for organization, the CLI can load a model from anywhere in the file system.

## Installation

- Install **[Python 3.13](https://www.python.org/downloads/)**
- Download **[llama.cpp](https://github.com/ggml-org/llama.cpp/releases/latest)**
- Optionally, to use image generation, download **[KoboldCpp](https://github.com/LostRuins/koboldcpp/releases/latest)** (if using AMD, get it from [here](https://github.com/YellowRoseCx/koboldcpp-rocm))
- Download the application and extract the folder
- Open the folder in **Terminal** and run `pip install -r requirements.txt`

## Usage

On run, `settings.json` will be automatically created. For the server startup phases, quoted paths are accepted.

This assumes you don't have **llama.cpp** open already:

```
# Must be a directory path and end with /.
# Expects llama-server.exe to be in the directory.
Enter the path to llama.cpp: C:/llama.cpp/

Enter the path to your desired text model: text_models/qwen3-4b-q8_0.gguf
```

If `script_mode` is set to `"chat"`, `enable_image_model_server_in_chat` is `true`, and **KoboldCpp** is not running:

```
# Must be a directory path and end with /.
# Expects koboldcpp.exe to be in the directory.
# For executables like koboldcpp_cu12.exe, rename them to the expected filename.
Enter the path to KoboldCpp: C:/KoboldCpp/

Enter the path to your desired image model: "image_models/sdxl.safetensors" or "C:/folder/sdxl-q4_0.gguf"

# For unquantized models (e.g., sd_1.5.safetensors).
# LoRA multiplier is capped to 0.0 minimum and 1.0 maximum.
Enter the path to the LoRA you want to apply to the image model (optional): C:/folder/sdxl_lora.safetensors
Enter the LoRA multiplier: 0.7
```

Once the text model server (and image model server) are started, you can interact with the AI.

## Language Models

When in doubt which `.gguf` to download, take your GPU VRAM and use the file size as a guideline. It's recommended to have a minimum of **16GB RAM** and **6GB VRAM**.

A model is considered multimodal if it follows this file structure:

```
# Example for Pixtral 12B
pixtral-12b-q4_k_m.gguf
pixtral-12b-q4_k_m-mmproj.gguf

# Example for Qwen2-Audio 7B
qwen2-audio-7b-iq4_xs.gguf
qwen2-audio-7b-iq4_xs-mmproj.gguf
```

Thus, if you download a multimodal projector for a model, you may need to rename it.

### Text-Only Models

- **[Qwen3 0.6B](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/main)**
  - Good for potato PCs.
- **[Qwen3 1.7B](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main)**
- **[Qwen3 4B](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/main)**
- **[Qwen3 8B](https://huggingface.co/Qwen/Qwen3-8B-GGUF/tree/main)**
- **[Gemma 3 1B](https://huggingface.co/unsloth/gemma-3-1b-it-GGUF/tree/main)**
  - Good for potato PCs.

### Multimodal Models

- **[Qwen2-Audio 7B](https://huggingface.co/mradermacher/Qwen2-Audio-7B-Instruct-GGUF/tree/main)**
  - Make sure to download both the model and multimodal projector (f16/Q8_0).
- **[Gemma 3 4B](https://huggingface.co/unsloth/gemma-3-4b-it-qat-GGUF/tree/main)**
  - Make sure to download the multimodal projector (f32/f16/bf16).
- **[Tiger Gemma 12B v3](https://huggingface.co/TheDrummer/Tiger-Gemma-12B-v3-GGUF/tree/main)**
  - Less censored version of **Gemma 3 12B**.
  - Get the multimodal projector from [here](https://huggingface.co/koboldcpp/mmproj/resolve/main/gemma3-12b-mmproj.gguf?download=true).

## Image Models

**Stable Diffusion (1.5, XL)** models will be primarily talked about here; they are often provided as `.safetensors` files, which take up a lot of memory when loaded. If you want to run one alongside the LM and your hardware isn't powerful enough, you may need to quantize the image model.

To quantize image models, you'll need **[stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp/releases/latest)**. Alternatively, you can get a pre-quantized image model from [here](https://huggingface.co/koboldcpp/imgmodel/tree/main).

---

# Documentation

## Settings

- `script_mode`: Determines how you can interact with the AI.
  - **Type:** `str`
  - **Values:** `"chat"`, `"autocomplete"`
- `text_model_init_settings`: These settings apply to newly started **llama.cpp** instances.
  - `server_port`: The port the server should run on.
    - **Type:** `int`
    - **Min. Value:** `1000`
    - **Max. Value:** `9999`
  - `priority`: Set the server process priority.
    - **Type:** `int`
    - **Values:** `0` (normal), `1` (medium), `2` (high), `3` (real-time)
  - `use_flash_attention`: Enable Flash Attention.
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `gpu_layers`: Amount of layers to offload to the GPU.
    - **Type:** `int`
    - **Min. Value:** `0`
  - `use_gpu_for_mmproj`: Offload the multimodal projector to the GPU.
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `use_continuous_batching`: Enable continuous batching (also known as dynamic batching).
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `logical_max_batch_size`: Logical maximum batch size.
    - **Type:** `int`
    - **Min. Value:** `16`
  - `physical_max_batch_size`: Physical maximum batch size.
    - **Type:** `int`
    - **Min. Value:** `4`
  - `cache_type_k`: KV cache data type for K.
    - **Type:** `str`
    - **Values:** `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
  - `cache_type_v`: KV cache data type for V.
    - **Type:** `str`
    - **Values:** `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
  - `cache_defragmentation_threshold`: KV cache defragmentation threshold.
    - **Type:** `float`
  - `cache_reuse_size`: Refer to https://ggml.ai/f0.png.
    - **Type:** `int`
    - **Min. Value:** `0`
  - `use_context_shift`: Enable Context Shift. Note that **llama.cpp** automatically disables Context Shift for some models (e.g., **Gemma 3**).
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `context_size`: Maximum amount of tokens the text model can handle.
    - **Type:** `int`
    - **Min. Value:** `256`
  - `disable_mmproj`: Disable multimodal projector loading.
    - **Type:** `bool`
    - **Values:** `true`, `false`
- `text_model_gen_settings`: These settings apply to language model text generation. If you change any of these settings at runtime, you must restart the script.
  - `stream_responses`: Allows receiving each predicted token in real-time.
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `temperature`: Adjust the randomness of the generated text.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `2.0`
  - `top_k`: Limit the next token selection to the K most probable tokens.
    - **Type:** `int`
    - **Min. Value:** `0`
    - **Max. Value:** `100`
  - `top_p`: Limit the next token selection to a subset of tokens with a cumulative probability above a threshold P.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `1.0`
  - `min_p`: The minimum probability for a token to be considered, relative to the probability of the most likely token.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `1.0`
  - `typical_p`: Enable locally typical sampling with parameter P.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `1.0`
  - `repetition_penalty`: Control the repetition of token sequences in the generated text.
    - **Type:** `float`
    - **Min. Value:** `1.0`
    - **Max. Value:** `2.0`
  - `repetition_penalty_range`: Amount of recent tokens to consider for penalizing repetition. If `0`, this is disabled. If `1`, this will extend to the available context size.
    - **Type:** `int`
    - **Min. Value:** `-1`
    - **Max. Value:** `8192`
  - `presence_penalty`: Repeat alpha presence penalty.
    - **Type:** `float`
    - **Min. Value:** `-2.0`
    - **Max. Value:** `2.0`
  - `frequency_penalty`: Repeat alpha frequency penalty.
    - **Type:** `float`
    - **Min. Value:** `-2.0`
    - **Max. Value:** `2.0`
  - `dry_base`: Set the Don't Repeat Yourself (DRY) repetition penalty base value.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `8.0`
  - `dry_multiplier`: Set the DRY repetition penalty multiplier.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `100.0`
  - `dry_allowed_length`: Tokens that extend repetition beyond this receive exponentially increasing penalty: `multiplier * base ^ (length of repeating sequence before token - allowed length)`.
    - **Type:** `int`
    - **Min. Value:** `0`
    - **Max. Value:** `100`
  - `xtc_probability`: Set the chance for token removal via Exclude Top Choices (XTC) sampler.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `1.0`
  - `xtc_threshold`: Set a minimum probability threshold for tokens to be removed via XTC sampler.
    - **Type:** `float`
    - **Min. Value:** `0.0`
    - **Max. Value:** `1.0`
  - `chat_show_thoughts_in_nonstreaming_mode`: If `text_model_gen_settings.stream_responses` is `false` and this is `false`, `<think>` blocks will not be displayed. This is a Chat Mode-specific setting.
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `chat_include_thoughts_in_history`: Whether to include `<think>` blocks in the message history. This is a Chat Mode-specific setting.
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `autocomplete_max_tokens`: Amount of tokens to generate in Autocomplete Mode.
    - **Type:** `int`
    - **Min. Value:** `16`
    - **Max. Value:** `1024`
- `enable_image_model_server_in_chat`: Enables image generation capabilities in Chat Mode. This doesn't modify the system prompt, but rather it allows usage of the command `/image`.
  - **Type:** `bool`
  - **Values:** `true`, `false`
- `image_model_init_settings`: These settings apply to newly started **KoboldCpp** instances.
  - `server_port`: The port the server should run on.
    - **Type:** `int`
    - **Min. Value:** `1000`
    - **Max. Value:** `9999`
  - `hardware_acceleration`: If set to `none`, the model will not utilize the GPU.
    - **Type:** `str`
    - **Values:** `none`, `cuda`, `clblast`, `vulkan`
  - `quantize_safetensors_on_server_start`: Quantize `.safetensors` models on server startup (drastically increases the load time).
    - **Type:** `bool`
    - **Values:** `true`, `false`
  - `use_vae_tiling`: Enable VAE tiling. `false` may not work for large images.
    - **Type:** `bool`
    - **Values:** `true`, `false`
- `open_image_output_on_gen`: Automatically open generated images.
  - **Type:** `bool`
  - **Values:** `true`, `false`

## Chat Mode

Chat with the AI. You can send files (text files, images, audio) in the chat; the `/attach` command is stripped from your message so as to not pollute the context. The ability to send images/audio files depends on the LM's multimodal capabilities.

Generated images are saved to the `image_outputs` folder. Provided that the LM is vision-enabled, they can also be part of the context.

**Usage Example:**

~~~
USER: What is the capital of France?

MODEL: The capital of France is Paris.

USER: Next, read this file. /attach
Enter the path to the file that will be attached to your message: chat_system_prompt.txt

MODEL: I have read the `chat_system_prompt.txt` file. The content of the file is:

```
You are a helpful assistant.
```

USER: 
~~~

**Commands:**

- `/image`: Generate an image (requires the image model server to be online).
- `/attach`: Attach a file or image URL to your message (command must be at the end of your message).
- `/help`: Show all commands.
- `/exit`: Exit the application.

**Supported Attachments:**

- **Generic:** Refer to `TEXT_MODEL_ATTACHMENT_GENERIC_FILENAMES` and `TEXT_MODEL_ATTACHMENT_GENERIC_EXTENSIONS` in `app.py` (too many to list here).
- **Images:** `JPEG, JPEG XL, JPEG LS, JPEG XR, PNG, TIFF, WebP`
- **Audio:** `WAV, MP3`

## Autocomplete Mode

Input a prompt and the AI will continue it. Context is not maintained in this mode.

**Usage Example:**

```
> Hello
Hello World!

> 
```