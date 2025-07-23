import json

if __name__ == "__main__":
    SCRIPT_SETTINGS_PATH: str = "settings.json"
    IMAGE_MODEL_GEN_SETTINGS_PRESETS: dict[str, dict] = {
        "default": {
            "cfg_scale": 5,
            "steps": 20,
            "width": 512,
            "height": 512,
            "seed": -1,
            "clip_skip": -1,
            "sampler_name": "Euler a",
        },
    }

    try:
        with open(SCRIPT_SETTINGS_PATH, "rt") as file:
            script_settings: dict = json.load(file)
            if "image_model_gen_settings" not in script_settings:
                print("Malformed settings file")
                exit()

        available_presets: str = ""
        for key in IMAGE_MODEL_GEN_SETTINGS_PRESETS.keys():
            available_presets += f"{key}, "
        available_presets = available_presets.removesuffix(", ")
        print(f"Presets: {available_presets}")

        preset: str = input("\nEnter a image_model_gen_settings preset: ").strip()
        if preset in IMAGE_MODEL_GEN_SETTINGS_PRESETS:
            for key, value in IMAGE_MODEL_GEN_SETTINGS_PRESETS[preset].items():
                script_settings["image_model_gen_settings"][key] = value
            with open(SCRIPT_SETTINGS_PATH, "wt") as file:
                json.dump(script_settings, file, indent=4)
        else:
            print(f"Preset '{preset}' is invalid")
    except FileNotFoundError:
        print("Settings file not found")
    except UnicodeDecodeError:
        print("Settings file is unreadable")
    except json.JSONDecodeError:
        print("Malformed settings file")