import json
import os
import tkinter as tk
from tkinter import messagebox

from path import Path
from serializer import Serializer


class SampleMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx
        ezg = ctx.cfg.easy_zatu_gen

        self.sample_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["sample_menu"], menu=self.sample_menu)
        self.sample_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.sample_menu.delete(0, tk.END)

        if not self.ctx.cfg.easy_zatu_gen["confirm_nsfw"]:
            if messagebox.askyesno(message=self.ctx.l10n["dlg_confirm_nsfw"]):
                os.system(f"curl -Lo {Path.sample_nsfw} https://yyy.wpx.jp/EasyZatuGen/config/sample_nsfw.json")
            self.ctx.cfg.easy_zatu_gen["confirm_nsfw"] = True

        sample_json = None
        if os.path.exists(Path.sample):
            with open(Path.sample, "r", encoding="utf-8-sig") as f:
                sample_json = json.load(f)

        sample_nsfw_json = None
        if os.path.exists(Path.sample_nsfw):
            with open(Path.sample_nsfw, "r", encoding="utf-8-sig") as f:
                sample_nsfw_json = json.load(f)

        categories = {}
        if sample_json is not None:
            self.create_categories_menu(self.sample_menu, categories, sample_json)
        if sample_nsfw_json is not None:
            self.create_categories_menu(self.sample_menu, categories, sample_nsfw_json)

        self.sample_menu.add_separator()

        if sample_json is not None:
            for sample_name in sample_json["samples"]:
                self.create_sample_menu(categories, sample_name, sample_json["samples"][sample_name])

        if sample_nsfw_json is not None:
            for sample_name in sample_nsfw_json["samples"]:
                self.create_sample_menu(categories, sample_name, sample_nsfw_json["samples"][sample_name])

    def create_categories_menu(self, parent, categories, sample_json):
        for category in sample_json["categories"]:
            if category not in categories:
                categories[category] = tk.Menu(parent, tearoff=False)
                parent.add_cascade(label=category, menu=categories[category])

    def create_sample_menu(self, categories, sample_name, sample):
        parent = self.sample_menu
        if ("category" in sample) and (sample["category"] in categories):
            parent = categories[sample["category"]]
        parent.add_command(label=sample_name, command=lambda s=sample: Serializer.deserialize(self.ctx, s))
