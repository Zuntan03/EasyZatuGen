import tkinter as tk

from path import Path


class LogMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx

        self.log_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["log_menu"], menu=self.log_menu)
        self.log_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.log_menu.delete(0, "end")
        sd = self.ctx.cfg.stable_diffusion
        spc = self.ctx.cfg.speech
        ezg = self.ctx.cfg.easy_zatu_gen
        l10n = self.ctx.l10n

        # チャットログ
        def set_llm_output(*args):
            ezg["enable_llm_output_log"] = self.llm_output_var.get()

        self.llm_output_var = tk.BooleanVar(value=ezg["enable_llm_output_log"])
        self.llm_output_var.trace_add("write", set_llm_output)
        self.log_menu.add_checkbutton(label=l10n["log_llm_output"], variable=self.llm_output_var)

        # 画像プロンプトログ
        def set_image_prompt(*args):
            sd["enable_image_prompt_log"] = self.image_prompt_var.get()

        self.image_prompt_var = tk.BooleanVar(value=sd["enable_image_prompt_log"])
        self.image_prompt_var.trace_add("write", set_image_prompt)
        self.log_menu.add_checkbutton(label=l10n["log_image_prompt"], variable=self.image_prompt_var)

        # 画像プロンプト和訳ログ
        def set_translated_image_prompt(*args):
            sd["enable_translated_image_prompt_log"] = self.translated_image_prompt_var.get()

        self.translated_image_prompt_var = tk.BooleanVar(value=sd["enable_translated_image_prompt_log"])
        self.translated_image_prompt_var.trace_add("write", set_translated_image_prompt)
        self.log_menu.add_checkbutton(
            label=l10n["log_translated_image_prompt"], variable=self.translated_image_prompt_var
        )

        # 読み上げログ
        def set_speech_log(*args):
            spc["enable_speech_log"] = self.speech_log_var.get()

        self.speech_log_var = tk.BooleanVar(value=spc["enable_speech_log"])
        self.speech_log_var.trace_add("write", set_speech_log)
        self.log_menu.add_checkbutton(label=l10n["log_speech"], variable=self.speech_log_var)

        # パフォーマンスログ
        def set_performance_log(*args):
            ezg["enable_perf_log"] = self.performance_log_var.get()

        self.performance_log_var = tk.BooleanVar(value=ezg["enable_perf_log"])
        self.performance_log_var.trace_add("write", set_performance_log)
        self.log_menu.add_checkbutton(label=l10n["log_performance"], variable=self.performance_log_var)
