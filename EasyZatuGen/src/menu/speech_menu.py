import subprocess
import tkinter as tk
from tkinter import messagebox

import requests
from path import Path


class SpeechMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx
        self.chars = ["main_char", "sub_char", "narrator"]

        self.speech_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["speech_menu"], menu=self.speech_menu)
        self.speech_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.speech_menu.delete(0, tk.END)
        cfg = self.ctx.cfg.speech
        l10n = self.ctx.l10n

        # 有効
        def set_speech_enable(*args):
            cfg["enable"] = self.speech_enable_var.get()

        self.speech_enable_var = tk.BooleanVar(value=cfg["enable"])
        self.speech_enable_var.trace_add("write", set_speech_enable)
        self.speech_menu.add_checkbutton(label=l10n["speech_enable"], variable=self.speech_enable_var)

        # 音量
        volume_menu = tk.Menu(self.speech_menu, tearoff=0)
        self.speech_menu.add_cascade(label=l10n["speech_play_volume"].format(cfg["play_volume"]), menu=volume_menu)

        def set_volume(volume):
            cfg["play_volume"] = volume
            self.speech_menu.entryconfigure(1, label=l10n["speech_play_volume"].format(volume))

        volumes = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
        for volume in volumes:
            volume_menu.add_command(label=f"{volume}%", command=lambda v=volume: set_volume(v))

        # 間隔
        interval_menu = tk.Menu(self.speech_menu, tearoff=0)
        self.speech_menu.add_cascade(
            label=l10n["speech_play_interval"].format(cfg["play_interval"]), menu=interval_menu
        )

        def set_interval(interval):
            cfg["play_interval"] = interval
            self.speech_menu.entryconfigure(2, label=l10n["speech_play_interval"].format(interval))

        intervals = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for interval in intervals:
            label = l10n["speech_play_interval_item"].format(interval)
            interval_menu.add_command(label=label, command=lambda i=interval: set_interval(i))

        # 最大生成トークン数
        max_new_tokens_menu = tk.Menu(self.speech_menu, tearoff=0)
        self.speech_menu.add_cascade(
            label=l10n["speech_max_new_tokens"].format(cfg["max_new_tokens"]), menu=max_new_tokens_menu
        )

        def set_max_new_tokens(max_new_tokens):
            cfg["max_new_tokens"] = max_new_tokens
            self.speech_menu.entryconfigure(3, label=l10n["speech_max_new_tokens"].format(max_new_tokens))

        tokens = [64, 96, 128, 192, 256, 512, 1024]
        for token in tokens:
            max_new_tokens_menu.add_command(label=str(token), command=lambda t=token: set_max_new_tokens(t))

        self.speech_enable_var.set(cfg["enable"])

        if not cfg["enable"]:
            return

        models_info = None
        failed = False
        try:
            base_url = f"http://{cfg['server']}:{cfg['port']}"
            headers = {"accept": "application/json"}
            result = requests.get(f"{base_url}/models/info", headers=headers)
            failed = result.status_code != 200
            models_info = result.json()
        except Exception as e:
            failed = True
        if failed:
            self.speech_enable_var.set(False)
            msg_result = messagebox.askyesno(None, l10n["dlg_launch_speech_server"])
            if msg_result:
                # subprocess.CREATE_NEW_PROCESS_GROUP, subprocess.DETACHED_PROCESS でプロセス分離できず
                subprocess.run([Path.launch_speech_server_bat])
            return

        voice_names = []
        voice_styles = {}
        for model_id in models_info:
            model = models_info[model_id]
            voice_name = model["config_path"][len("model_assets\\") : -len("\\config.json")]
            voice_names.append(voice_name)
            voice_styles[voice_name] = list(model["style2id"])

        def set_voice(char, voice_name):
            cfg[f"{char}_voice"] = voice_name
            cfg[f"{char}_style"] = "Neutral"

        def set_voice_style(char, voice_style):
            cfg[f"{char}_style"] = voice_style

        def set_voice_style_weight(char, voice_style_weight):
            cfg[f"{char}_style_weight"] = voice_style_weight

        style_weights = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        for char in self.chars:
            self.speech_menu.add_separator()

            char_voice_name = cfg[f"{char}_voice"]
            char_menu = tk.Menu(self.speech_menu, tearoff=0)
            char_menu_label = l10n[f"speech_{char}_voice"].format(char_voice_name)
            self.speech_menu.add_cascade(label=char_menu_label, menu=char_menu)

            for voice_name in voice_names:
                check_var = tk.BooleanVar(value=(voice_name == char_voice_name))
                check_var.trace_add("write", lambda *args, var=check_var, c=char, v=voice_name: set_voice(c, v))
                char_menu.add_checkbutton(label=voice_name, variable=check_var)

            char_style_menu = tk.Menu(self.speech_menu, tearoff=0)
            char_style_menu_label = l10n[f"speech_{char}_style"].format(cfg[f"{char}_style"])
            self.speech_menu.add_cascade(label=char_style_menu_label, menu=char_style_menu)
            for voice_style in voice_styles[char_voice_name]:
                check_var = tk.BooleanVar(value=(voice_style == cfg[f"{char}_style"]))
                check_var.trace_add("write", lambda *args, var=check_var, c=char, v=voice_style: set_voice_style(c, v))
                char_style_menu.add_checkbutton(label=voice_style, variable=check_var)

            char_style_weight_menu = tk.Menu(self.speech_menu, tearoff=0)
            char_style_weight_menu_label = l10n[f"speech_{char}_style_weight"].format(cfg[f"{char}_style_weight"])
            self.speech_menu.add_cascade(label=char_style_weight_menu_label, menu=char_style_weight_menu)
            for style_weight in style_weights:
                check_var = tk.BooleanVar(value=(style_weight == cfg[f"{char}_style_weight"]))
                check_var.trace_add(
                    "write", lambda *args, var=check_var, c=char, v=style_weight: set_voice_style_weight(c, v)
                )
                char_style_weight_menu.add_checkbutton(label=style_weight, variable=check_var)
