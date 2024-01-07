import json
import os
import subprocess
import tkinter as tk
from tkinter import filedialog

from path import Path


class ModelMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx
        self.sd = ctx.cfg.stable_diffusion

        self.model_menu = tk.Menu(form.win, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["model_menu"], menu=self.model_menu)
        self.model_menu.configure(postcommand=self.on_menu_open)

    def open_model(self):
        initialdir = os.path.dirname(self.get_model()["path"])
        if not os.path.exists(initialdir):
            initialdir = Path.cwd

        new_model_path = filedialog.askopenfilename(
            title=self.ctx.l10n["dlg_open_model_title"],
            filetypes=[(self.ctx.l10n["dlg_open_model_file"], "*.safetensors;*.ckpt")],
            initialdir=initialdir,
        )

        if new_model_path and os.path.exists(new_model_path):
            new_model_name = os.path.splitext(os.path.basename(new_model_path))[0]
            if new_model_name in self.sd["models"]:
                self.sd["models"].pop(new_model_name)
            new_model = {"path": new_model_path, "download_url": "", "information_url": ""}

            # civitai info から上書き
            info_path = os.path.splitext(new_model_path)[0] + ".civitai.info"

            info = None
            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)

            if info is not None:
                if "id" in info:
                    new_model["download_url"] = f'https://civitai.com/api/download/models/{info["id"]}/'
                if "modelId" in info:
                    new_model["information_url"] = f'https://civitai.com/models/{info["modelId"]}/'

            self.sd["models"][new_model_name] = new_model
            self.sd["model_name"] = new_model_name

    def get_model(self):
        model_name = self.sd["model_name"]
        models = self.sd["models"]
        if model_name in models:
            return models[model_name]
        else:
            if len(models) == 0:
                models["real_model_N"] = {"path": "model\\real_model_N.safetensors"}
            self.sd["model_name"] = list(models)[-1]
            return models[self.sd["model_name"]]

    def set_model(self, model_name):
        self.sd["model_name"] = model_name
        model = self.sd["models"].pop(model_name)
        self.sd["models"][model_name] = model

    def on_menu_open(self):
        self.model_menu.delete(0, tk.END)  # セパレータから消すとOpenイベントも消える？

        self.model_menu.add_command(label=self.ctx.l10n["model_open"], command=self.open_model)

        self.model_download_menu = tk.Menu(self.model_menu, tearoff=False)
        self.model_menu.add_cascade(label=self.ctx.l10n["model_download"], menu=self.model_download_menu)
        self.model_download_menu.configure(postcommand=self.on_download_menu_open)

        self.model_menu.add_separator()

        for model_name in reversed(list(self.sd["models"])):
            model = self.sd["models"][model_name]

            if os.path.exists(model["path"]):
                check_var = tk.BooleanVar(value=(model_name == self.sd["model_name"]))
                # lambda で var の引数指定が必要
                check_var.trace_add("write", lambda *args, name=model_name, var=check_var: self.set_model(name))
                self.model_menu.add_checkbutton(label=model_name, variable=check_var)
            else:
                del self.sd["models"][model_name]

    def on_download_menu_open(self):
        assert os.path.exists(Path.model_download)
        model_json = None
        with open(Path.model_download, "r", encoding="utf-8-sig") as frmd:
            model_json = json.load(frmd)

        self.model_download_menu.delete(0, tk.END)

        categories = {}
        for category_name in model_json["categories"]:
            categories[category_name] = tk.Menu(self.model_download_menu, tearoff=False)
            self.model_download_menu.add_cascade(label=category_name, menu=categories[category_name])

        self.model_download_menu.add_separator()

        def download_model(model_name, model):
            subprocess.run(["start", model["information_url"]], shell=True)
            cmd = f"curl -Lo {model['path']} {model['download_url']} || pause"
            result = subprocess.run(["start", "cmd", "/c", cmd], shell=True)  # 待たないので即成功
            if result.returncode == 0:
                if model_name in self.sd["models"]:
                    self.sd["models"].pop(model_name)
                self.sd["models"][model_name] = model

        for model_name in model_json["models"]:
            src_model = model_json["models"][model_name]
            dst_model = {
                "path": os.path.join(Path.model_dir, model_name + ".safetensors"),
                "download_url": src_model["download_url"],
                "information_url": src_model["information_url"],
            }
            parent = self.model_download_menu
            if "category" in src_model:
                if src_model["category"] in categories:
                    parent = categories[src_model["category"]]
            check_var = tk.BooleanVar(value=os.path.exists(dst_model["path"]))
            parent.add_checkbutton(
                label=model_name,
                command=lambda v=check_var, model_name=model_name, model=dst_model: download_model(model_name, model),
                variable=check_var,
            )
