import json

if __name__ == "__main__":
    SCRIPT_SETTINGS_PATH: str = "settings.json"
    TEXT_MODEL_GEN_SETTINGS_PRESETS: dict[str, dict] = {
        "default": {
            "temperature": 0.8,
            "top_k": 40,
            "top_p": 0.95,
            "min_p": 0.05,
            "typical_p": 1.0,
            "repetition_penalty": 1.1,
            "repetition_penalty_range": 64,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "dry_base": 1.75,
            "dry_multiplier": 0.0,
            "dry_allowed_length": 2,
            "xtc_probability": 0.0,
            "xtc_threshold": 0.1,
        },
        "qwen3_nothink": {
            "temperature": 0.6,
            "top_k": 20,
            "top_p": 0.95,
            "min_p": 0.0,
        },
        "qwen3_think": {
            "temperature": 0.7,
            "top_k": 20,
            "top_p": 0.8,
            "min_p": 0.0,
        },
    }

    try:
        with open(SCRIPT_SETTINGS_PATH, "rt") as file:
            script_settings: dict = json.load(file)
            if "text_model_gen_settings" not in script_settings:
                print("Malformed settings file")
                exit()

        available_presets: str = ""
        for key in TEXT_MODEL_GEN_SETTINGS_PRESETS.keys():
            available_presets += f"{key}, "
        available_presets = available_presets.removesuffix(", ")
        print(f"Presets: {available_presets}")

        preset: str = input("\nEnter a text_model_gen_settings preset: ").strip()
        if preset in TEXT_MODEL_GEN_SETTINGS_PRESETS:
            for key, value in TEXT_MODEL_GEN_SETTINGS_PRESETS[preset].items():
                script_settings["text_model_gen_settings"][key] = value
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