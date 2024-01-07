import json
import os
import shutil

from path import Path
from PIL import Image
from serializer import Serializer


class Context:
    l10n = None

    def __init__(self):
        self._load_config()

    def _load_config(self):
        class Config:
            pass

        self.cfg = Config()

        def load_json(config_name):
            config = {}
            default_config_path = os.path.join(Path.default_config_dir, f"{config_name}.json")
            assert os.path.exists(default_config_path)
            with open(default_config_path, "r", encoding="utf-8-sig") as frdc:
                config = json.load(frdc)

            config_path = os.path.join(Path.config_dir, f"{config_name}.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8-sig") as frc:
                    config.update(json.load(frc))
            else:
                with open(config_path, "w", encoding="utf-8-sig") as fwc:
                    json.dump(config, fwc, indent=4, ensure_ascii=False)
            setattr(self.cfg, config_name, config)
            return config

        def copy_json(config_name):
            config_path = os.path.join(Path.config_dir, f"{config_name}.json")
            default_config_path = os.path.join(Path.default_config_dir, f"{config_name}.json")
            shutil.copy2(default_config_path, config_path)

            config = {}
            with open(config_path, "r", encoding="utf-8-sig") as frc:
                config.update(json.load(frc))
            setattr(self.cfg, config_name, config)
            return config

        load_json("easy_zatu_gen")
        Context.l10n = copy_json(f'l10n_{self.cfg.easy_zatu_gen["lang"]}')
        self.l10n = Context.l10n

        load_json("speech")
        load_json("stable_diffusion")

        def copy_file(file_name):
            file_path = os.path.join(Path.config_dir, f"{file_name}")
            default_file_path = os.path.join(Path.default_config_dir, f"{file_name}")
            if not os.path.exists(file_path):
                shutil.copy2(default_file_path, file_path)
            else:
                if os.path.getmtime(default_file_path) > os.path.getmtime(file_path):
                    # TODO: テンプレートはバックアップする？
                    shutil.copy2(default_file_path, file_path)

        copy_file("speech_llm_template.txt")
        copy_file("stable_diffusion_llm_template.txt")
        copy_file("translate_llm_template.txt")

        copy_file("model_download.json")
        copy_file("lora_download.json")
        copy_file("sample.json")
        if os.path.exists(os.path.join(Path.default_config_dir, "sample_nsfw.json")):  # 開発用
            copy_file("sample_nsfw.json")

    def open_file(self, file_path):
        json_data = None
        if file_path.endswith(".png"):
            image = Image.open(file_path)
            json_data = image.info.get("ezzatugn")
        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8-sig") as f:
                json_data = f.read()
        if json_data is not None:
            Serializer.deserialize(self, json.loads(json_data))
            print(json_data)

    def reset_config(self):
        def load_default_config(config_name):
            config = {}
            default_config_path = os.path.join(Path.default_config_dir, f"{config_name}.json")
            assert os.path.exists(default_config_path)
            with open(default_config_path, "r", encoding="utf-8-sig") as frdc:
                config = json.load(frdc)
            return config

        self.cfg.easy_zatu_gen.update(load_default_config("easy_zatu_gen"))
        self.cfg.speech.update(load_default_config("speech"))
        sd = load_default_config("stable_diffusion")
        sd.pop("models", None)
        sd.pop("loras", None)
        self.cfg.stable_diffusion.update(sd)

        def copy_file(file_name):
            file_path = os.path.join(Path.config_dir, f"{file_name}")
            default_file_path = os.path.join(Path.default_config_dir, f"{file_name}")
            shutil.copy2(default_file_path, file_path)

        copy_file("speech_llm_template.txt")
        copy_file("stable_diffusion_llm_template.txt")
        copy_file("translate_llm_template.txt")

    def finalize(self):
        self.cfg.easy_zatu_gen["input"] = self.form.input_var.get()
        self.form.save_config(self)

        def save_json(config_name):
            config_path = os.path.join(Path.config_dir, f"{config_name}.json")
            with open(config_path, "w", encoding="utf-8-sig") as fwc:
                json.dump(getattr(self.cfg, config_name), fwc, indent=4, ensure_ascii=False)

        save_json("easy_zatu_gen")
        save_json("speech")
        save_json("stable_diffusion")

        self.form.win.destroy()
