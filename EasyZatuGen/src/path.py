import os
import re
from datetime import datetime


class Path:
    path_regex = re.compile(r'[\n\r<>:"/\\|?* ]')

    @classmethod
    def init(cls):
        cls.cwd = os.getcwd()
        cls.config_dir = os.path.join(cls.cwd, "config")
        cls.embedding_dir = os.path.join(cls.cwd, "embedding")
        cls.output_dir = os.path.join(cls.cwd, "output")

        cls.easy_zatu_gen_dir = os.path.join(cls.cwd, "EasyZatuGen")
        cls.res_dir = os.path.join(cls.easy_zatu_gen_dir, "res")
        cls.default_config_dir = os.path.join(cls.res_dir, "default_config")

        cls.model_dir = os.path.join(cls.cwd, "model")
        cls.lora_dir = os.path.join(cls.cwd, "lora")

        cls.speech_llm_template = os.path.join(cls.config_dir, "speech_llm_template.txt")
        cls.stable_diffusion_llm_template = os.path.join(cls.config_dir, "stable_diffusion_llm_template.txt")
        cls.translate_llm_template = os.path.join(cls.config_dir, "translate_llm_template.txt")

        cls.model_download = os.path.join(cls.config_dir, "model_download.json")
        cls.lora_download = os.path.join(cls.config_dir, "lora_download.json")
        cls.sample = os.path.join(cls.config_dir, "sample.json")
        cls.sample_nsfw = os.path.join(cls.config_dir, "sample_nsfw.json")

        cls.launch_speech_server_bat = os.path.join(cls.cwd, "SingleLaunch-StyleBertVITS2.bat")

        os.makedirs(cls.config_dir, exist_ok=True)

    @classmethod
    def open_dir(cls, path):
        os.system(f'explorer "{path}"')

    @classmethod
    def get_output_dir(cls):
        output_dir = os.path.join(".", "output", datetime.now().strftime("%Y%m%d"))  # TODO: 絶対パス
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    @classmethod
    def get_output_file_name(cls, suffix=""):
        return datetime.now().strftime("%Y%m%d-%H%M%S") + suffix

    @classmethod
    def get_output_path(cls, suffix=""):
        return os.path.join(cls.get_output_dir(), cls.get_output_file_name(suffix))

    @classmethod
    def get_path_name(cls, name):
        return cls.path_regex.sub("_", name).replace("___", "_").replace("__", "_")
