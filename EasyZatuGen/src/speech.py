import os
import re
import subprocess
import time

import requests
from context import Context
from job_queue import JobQueue
from path import Path
from perf import Perf


class Speech:
    eos_regex = re.compile(r"[、,。.？?！!\n]")

    def __init__(self):
        self.reset_generate_state()
        self.play_job = None

        self.generate_queue = JobQueue()
        self.play_queue = JobQueue()

    def reset_generate_state(self):
        self.llm_job = None
        self.args = None
        self.generate_jobs = []
        self.generate_job_index = 0

    def mainloop(self, ctx):
        cfg = ctx.cfg.speech
        self.generate_queue.update()
        self.play_queue.update()

        if not cfg["enable"]:
            return False

        if self.llm_job is None:
            self._generate_script(ctx)
        if (self.llm_job is None) or (not self.llm_job.successful()):
            return False

        if self.args is None:
            self._setup_args(ctx)
            if len(self.args["scripts"]) == 0:
                self.reset_generate_state()
                return False

        if len(self.generate_jobs) == self.generate_job_index:
            failed = False
            try:
                url = f'http://{cfg["server"]}:{cfg["port"]}/models/info'
                responce = requests.get(url, headers={"accept": "application/json"})
                failed = responce.status_code != 200
            except Exception as e:
                failed = True
            if failed:
                cfg["enable"] = False
                return False
            self.generate_jobs.append(
                self.generate_queue.push(
                    self.generate_voice, args=self.args, generate_job_index=self.generate_job_index
                )
            )

        if self.generate_jobs[self.generate_job_index].successful():
            if (self.play_job is None) or self.play_job.successful():
                wav_path = self.generate_jobs[self.generate_job_index].result
                self.play_job = self.play_queue.push(
                    self.play_wav, wav_path=wav_path, volume=cfg["play_volume"], interval=cfg["play_interval"]
                )
                self.generate_job_index += 1

        if self.generate_job_index == len(self.args["scripts"]):
            self.reset_generate_state()
            return True

        return False

    def _generate_script(self, ctx):
        self.theme = ctx.parser.theme
        self.main_char = ctx.parser.main_char
        if self.theme == "":
            return

        template = ""
        assert os.path.exists(Path.speech_llm_template)
        with open(Path.speech_llm_template, "r", encoding="utf-8-sig") as frdt:
            template = frdt.read()
        llm_prompt = template.format(theme=self.theme, main_char=self.main_char)
        cfg = ctx.cfg.speech
        self.llm_job = ctx.gpu_job_queue.push(
            ctx.llm.generate,
            prompt=llm_prompt,
            max_new_tokens=cfg["max_new_tokens"],
            top_k=cfg["top_k"],
            top_p=cfg["top_p"],
            temperature=cfg["temperature"],
            repetition_penalty=cfg["repetition_penalty"],
            info="speech_script",
        )

        def llm_callback(job):
            self.generated_prompt = job.result[len(job.args["prompt"]) :].strip().replace("\n\n", "\n")
            self.generated_prompt = f"{self.main_char}「" + self.generated_prompt
            # print(f"[Script]\n{self.generated_prompt}")

        self.llm_job.callback = llm_callback

    def _setup_args(self, ctx):
        sp = ctx.cfg.speech
        main_char = ctx.parser.main_char
        generated_prompt = self.generated_prompt

        self.args = {
            "server": sp["server"],
            "port": sp["port"],
            "auto_split": sp["auto_split"],
            "main_char_voice": sp["main_char_voice"],
            "sub_char_voice": sp["sub_char_voice"],
            "narrator_voice": sp["narrator_voice"],
            "scripts": self._parse_generated_prompt(generated_prompt, main_char, sp),
            "enable_speech_log": sp["enable_speech_log"],
        }

    def _parse_generated_prompt(self, generated_prompt, main_char, cfg):
        scripts = []
        script_chunks = generated_prompt.split("」")

        # 最終チャンクに開きカッコがあれば以降を削除し、文末まで詰める
        num_chunks = len(script_chunks)
        last_chunk = script_chunks[num_chunks - 1]
        last_chunk = last_chunk.split("「", 1)[0]
        last_matches = list(Speech.eos_regex.finditer(last_chunk))
        if len(last_matches) > 0:
            last_chunk = last_chunk[: last_matches[-1].end()]
        if last_chunk != "":
            script_chunks[num_chunks - 1] = last_chunk

        for chunk in script_chunks:
            # 開きカッコより前もしくは全てがナレーション、以降がセリフ
            chunk_pair = chunk.split("「", 1)
            narrator_chunk = chunk_pair[0]
            char_chunk = ""
            char_name = ""
            if len(chunk_pair) == 2:
                char_chunk = chunk_pair[1]
                char_name = "sub_char"
                if narrator_chunk.endswith(main_char) or narrator_chunk.endswith("\n"):
                    char_name = "main_char"
                    if len(main_char) > 0:
                        narrator_chunk = narrator_chunk[: -len(main_char)]
            if narrator_chunk != "":
                narrator_matches = list(Speech.eos_regex.finditer(narrator_chunk))
                if len(narrator_matches) > 0:
                    narrator_chunk = narrator_chunk[: narrator_matches[-1].end()]

            char_chunk = char_chunk.strip().replace("\n", "")
            if char_chunk == main_char:
                char_chunk = ""

            narrator_chunk = narrator_chunk.strip().replace("\n", "")
            if narrator_chunk == main_char:
                narrator_chunk = ""

            if narrator_chunk != "":
                scripts.append(
                    {
                        "text": narrator_chunk,
                        "char_name": "narrator",
                        "voice_name": cfg["narrator_voice"],
                        "style": cfg["narrator_style"],
                        "style_weight": cfg["narrator_style_weight"],
                        "sdp_ratio": cfg["narrator_sdp_ratio"],
                        "noise": cfg["narrator_noise"],
                        "noisew": cfg["narrator_noisew"],
                        "length": cfg["narrator_length"],
                    }
                )
            if char_chunk != "":
                scripts.append(
                    {
                        "text": char_chunk,
                        "char_name": char_name,
                        "voice_name": cfg[f"{char_name}_voice"],
                        "style": cfg[f"{char_name}_style"],
                        "style_weight": cfg[f"{char_name}_style_weight"],
                        "sdp_ratio": cfg[f"{char_name}_sdp_ratio"],
                        "noise": cfg[f"{char_name}_noise"],
                        "noisew": cfg[f"{char_name}_noisew"],
                        "length": cfg[f"{char_name}_length"],
                    }
                )
        return scripts

    def generate_voice(self, args, generate_job_index):
        base_url = f"http://{args['server']}:{args['port']}"
        headers = {"accept": "application/json"}

        script = args["scripts"][generate_job_index]
        char_name = script["char_name"]
        voice_name = script["voice_name"]
        text = script["text"]

        voice_param = {
            "text": text,
            "model_id": 0,
            "speaker_id": 0,
            "auto_split": args["auto_split"],
            "style": script["style"],
            "style_weight": script["style_weight"],
            "sdp_ratio": script["sdp_ratio"],
            "noise": script["noise"],
            "noisew": script["noisew"],
            "length": script["length"],
        }

        while True:
            try:
                start_time = Perf.start()
                model_id = -1
                result = requests.get(f"{base_url}/models/info", headers=headers)
                if result.status_code == 200:
                    models_info = result.json()
                    for model_info_id in models_info:
                        model_info = models_info[model_info_id]
                        if model_info["config_path"][len("model_assets\\") : -len("\\config.json")] == voice_name:
                            model_id = int(model_info_id)
                            break
                if model_id == -1:
                    model_id = 0
                    voice_param["style"] = "Neutral"

                voice_param["model_id"] = model_id
                voice = requests.get(f"{base_url}/voice", params=voice_param, headers={"accept": "audio/wav"})
                path = Path.get_output_path(f"-{Path.get_path_name(text[:128])}.wav")
                with open(path, "wb") as fwb:
                    fwb.write(voice.content)
                Perf.end(start_time, f'Speech.generate("{voice_name}")')
                if args["enable_speech_log"]:
                    print(
                        Context.l10n["print_speech"].format(
                            char_name, voice_name, voice_param["style"], voice_param["style_weight"], text
                        )
                    )
                return path
            except Exception as e:
                print(e)
            time.sleep(1.0)

    def play_wav(self, wav_path, volume, interval):
        subprocess.Popen(
            ["ffplay", "-volume", f"{volume}", "-autoexit", "-nodisp", "-loglevel", "fatal", wav_path],
            stdout=subprocess.DEVNULL,  # 終了時の改行対策、stderrは残す
        ).wait()
        time.sleep(interval)
