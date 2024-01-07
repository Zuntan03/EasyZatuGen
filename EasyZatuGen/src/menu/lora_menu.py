import json
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, scrolledtext, ttk

from path import Path


class LoraMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx
        self.sd = ctx.cfg.stable_diffusion

        self.lora_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["lora_menu"], menu=self.lora_menu)
        self.lora_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.lora_menu.delete(0, "end")

        self.lora_menu.add_command(label=self.ctx.l10n["lora_edit"], command=self.open_lora_editor)
        self.lora_menu.add_separator()
        self.lora_menu.add_command(label=self.ctx.l10n["lora_open"], command=self.open_lora)

        self.lora_download_menu = tk.Menu(self.lora_menu, tearoff=False)
        self.lora_menu.add_cascade(label=self.ctx.l10n["lora_download"], menu=self.lora_download_menu)
        self.lora_download_menu.configure(postcommand=self.on_download_menu_open)

        self.lora_menu.add_separator()

        for lora_name in reversed(list(self.sd["loras"])):
            lora = self.sd["loras"][lora_name]
            if os.path.exists(lora["path"]):
                check_var = tk.BooleanVar(value=(lora_name in self.sd["lora_names"]))
                # lambda で var の引数指定が必要
                check_var.trace_add("write", lambda *args, name=lora_name, var=check_var: self.select_lora(name))
                # label = f'{lora_name}, TE:{lora["text_encoder_weight"]}, UNet:{lora["unet_weight"]}'# BUG: TE Wegight
                label = f'{lora_name}: {lora["unet_weight"]}'
                self.lora_menu.add_checkbutton(label=label, variable=check_var)
            else:
                del self.sd["loras"][lora_name]

    def open_lora(self):
        initialdir = Path.cwd
        if len(self.sd["loras"]) > 0:
            last_lora_name = list(self.sd["loras"])[-1]
            lora_path = os.path.dirname(self.sd["loras"][last_lora_name]["path"])
            if os.path.exists(lora_path):
                initialdir = lora_path

        new_lora_path = filedialog.askopenfilename(
            title=self.ctx.l10n["dlg_open_lora_title"],
            filetypes=[(self.ctx.l10n["dlg_open_lora_file"], "*.safetensors")],
            initialdir=initialdir,
        )
        if new_lora_path and os.path.exists(new_lora_path):
            new_lora_name = os.path.splitext(os.path.basename(new_lora_path))[0]
            new_lora = self.get_lora(new_lora_name, new_lora_path)
            if new_lora is None:
                return

            if new_lora_name in self.sd["loras"]:
                self.sd["loras"].pop(new_lora_name)
            self.sd["loras"][new_lora_name] = new_lora

            if new_lora_name in self.sd["lora_names"]:
                self.sd["lora_names"].remove(new_lora_name)
            self.sd["lora_names"].append(new_lora_name)  # self.sd["lora_names"].insert(0, new_lora_name)
            self.open_lora_editor()

    def get_lora(self, lora_name, lora_path):
        result = {
            "path": lora_path,
            "text_encoder_weight": 1.0,
            "unet_weight": 1.0,
            "trigger_prompt": "",
            "original_trigger_prompt": "",
            "download_url": "",
            "information_url": "",
        }

        # civitai info から上書き
        info_path = os.path.splitext(lora_path)[0] + ".civitai.info"
        info = None
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)

        if info is None:
            return result

        if "trainedWords" in info:
            trigger_prompt = ", \n".join(info["trainedWords"])
            result["trigger_prompt"] = trigger_prompt[: self.sd["lora_trigger_prompt_max_length"]]
            result["original_trigger_prompt"] = trigger_prompt

        if "id" in info:
            result["download_url"] = f'https://civitai.com/api/download/models/{info["id"]}/'

        if "modelId" in info:
            result["information_url"] = f'https://civitai.com/models/{info["modelId"]}/'

        return result

    def on_download_menu_open(self):
        assert os.path.exists(Path.lora_download)
        lora_json = None
        with open(Path.lora_download, "r", encoding="utf-8-sig") as f:
            lora_json = json.load(f)

        self.lora_download_menu.delete(0, tk.END)

        categories = {}
        for category_name in lora_json["categories"]:
            categories[category_name] = tk.Menu(self.lora_download_menu, tearoff=False)
            self.lora_download_menu.add_cascade(label=category_name, menu=categories[category_name])

        self.lora_download_menu.add_separator()

        def download_lora(lora_name, lora):
            if "download_url" in lora:
                if "information_url" in lora:
                    webbrowser.open(lora["information_url"], new=1)
                result = os.system(f"curl -Lo {lora['path']} {lora['download_url']} || pause")
                if result == 0:
                    if lora_name in self.sd["loras"]:
                        self.sd["loras"].pop(lora_name)
                    self.sd["loras"][lora_name] = lora

                    if lora_name in self.sd["lora_names"]:
                        self.sd["lora_names"].remove(lora_name)
                    self.sd["lora_names"].append(lora_name)

                    self.open_lora_editor()

        for lora_name in lora_json["loras"]:
            src_lora = lora_json["loras"][lora_name]
            dst_lora = {
                "path": os.path.join(Path.lora_dir, lora_name + ".safetensors"),
                "text_encoder_weight": src_lora["text_encoder_weight"],
                "unet_weight": src_lora["unet_weight"],
                "trigger_prompt": src_lora["trigger_prompt"],
                "original_trigger_prompt": src_lora["original_trigger_prompt"],
                "download_url": src_lora["download_url"],
                "information_url": src_lora["information_url"],
            }
            parent = self.lora_download_menu
            if "category" in src_lora:
                if src_lora["category"] in categories:
                    parent = categories[src_lora["category"]]
            check_var = tk.BooleanVar(value=os.path.exists(dst_lora["path"]))
            parent.add_checkbutton(
                label=lora_name,
                command=lambda v=check_var, lora_name=lora_name, lora=dst_lora: download_lora(lora_name, lora),
                variable=check_var,
            )

    def select_lora(self, lora_name):
        if lora_name in self.sd["lora_names"]:
            self.sd["lora_names"].remove(lora_name)
        else:
            self.sd["lora_names"].append(lora_name)  # self.sd["lora_names"].insert(0, lora_name)
            lora = self.sd["loras"].pop(lora_name)
            self.sd["loras"][lora_name] = lora

    def open_lora_editor(self):
        weight_max = 2.0
        min_w, min_h = 320, 400
        padx, pady = 4, 2
        lora_names = list(self.sd["loras"])
        lora_names.reverse()
        lora_name = lora_names[0]

        l10n = self.ctx.l10n
        lora_editor = tk.Toplevel(self.form.win)
        lora_editor.title(l10n["lora_editor_title"])
        lora_editor.minsize(min_w, min_h)
        lora_editor.geometry(f"{min_w}x{min_h}")

        def listup_lora():
            loras = list(self.sd["loras"])
            loras.reverse()
            cmb_lora_name["values"] = loras

        # LoRA 選択時の初期化
        def select_lora(lora_name):
            lora = self.sd["loras"][lora_name]

            te_weight = lora["text_encoder_weight"]
            unet_weight = lora["unet_weight"]
            sync_weight = te_weight == unet_weight
            sync_weight = True  # BUG: TE Wegight

            sync_weight_var.set(sync_weight)
            scl_text_encoder_weight.set(te_weight)
            scl_unet_weight.set(unet_weight)

            stx_trigger_prompt.delete("1.0", tk.END)
            stx_trigger_prompt.insert("1.0", lora["trigger_prompt"])
            stx_trigger_prompt.edit_modified(False)

            stx_original_trigger_prompt.configure(state=tk.NORMAL)
            stx_original_trigger_prompt.delete("1.0", tk.END)
            stx_original_trigger_prompt.insert("1.0", lora["original_trigger_prompt"])
            stx_original_trigger_prompt.configure(state=tk.DISABLED)

        # LoRA 選択
        lbl_select_lora = tk.Label(lora_editor, text=l10n["lora_editor_select_lora"])
        lbl_select_lora.pack(padx=padx, pady=pady, anchor="w")
        cmb_lora_name = ttk.Combobox(lora_editor, values=lora_names, postcommand=listup_lora, state="readonly")  #
        cmb_lora_name.bind("<<ComboboxSelected>>", lambda e: select_lora(cmb_lora_name.get()))
        cmb_lora_name.set(lora_name)
        cmb_lora_name.pack(fill=tk.X, padx=padx, pady=pady)

        # テキストエンコーダーの重み
        def changed_text_encoder_weight(e):
            lora = self.sd["loras"][cmb_lora_name.get()]
            lora["text_encoder_weight"] = scl_text_encoder_weight.get()
            # 同期対応
            if sync_weight_var.get():
                scl_unet_weight.configure(state=tk.NORMAL)
                scl_unet_weight.set(scl_text_encoder_weight.get())
                scl_unet_weight.configure(state=tk.DISABLED)
                lora["unet_weight"] = scl_text_encoder_weight.get()
            self.ctx.stable_diffusion.lora_changed = True

        lbl_text_encoder_weight = tk.Label(lora_editor, text=l10n["lora_editor_text_encoder_weight"])
        lbl_text_encoder_weight.pack(padx=padx, pady=pady, anchor="w")
        scl_text_encoder_weight = tk.Scale(
            lora_editor,
            orient=tk.HORIZONTAL,
            from_=-weight_max,
            to=weight_max,
            resolution=0.1,
            showvalue=True,
            command=changed_text_encoder_weight,
        )
        scl_text_encoder_weight.pack(fill=tk.X, padx=padx, pady=pady)

        # U-NET の重み
        def sync_weight_changed():
            sync_weight = sync_weight_var.get()
            scl_unet_weight.configure(state=tk.NORMAL)
            if sync_weight:
                scl_unet_weight.set(scl_text_encoder_weight.get())
                scl_unet_weight.configure(state=tk.DISABLED)
                lora = self.sd["loras"][cmb_lora_name.get()]
                lora["unet_weight"] = scl_text_encoder_weight.get()

        def changed_unet_weight(e):
            lora = self.sd["loras"][cmb_lora_name.get()]
            lora["unet_weight"] = scl_unet_weight.get()
            self.ctx.stable_diffusion.lora_changed = True

        lbl_unet_weight = tk.Label(lora_editor, text=l10n["lora_editor_unet_weight"])
        # lbl_unet_weight.pack(padx=padx, pady=pady, anchor="w")# BUG: TE Wegight
        sync_weight_var = tk.BooleanVar()
        sync_weight_var.trace_add("write", lambda *args: sync_weight_changed())
        chk_sync_weight = tk.Checkbutton(lora_editor, text=l10n["lora_editor_sync_weight"], variable=sync_weight_var)
        # chk_sync_weight.pack(padx=padx, pady=pady, anchor="w")# BUG: TE Wegight
        scl_unet_weight = tk.Scale(
            lora_editor,
            orient=tk.HORIZONTAL,
            from_=-weight_max,
            to=weight_max,
            resolution=0.1,
            showvalue=True,
            command=changed_unet_weight,
        )
        # scl_unet_weight.pack(fill=tk.X, padx=padx, pady=pady)# BUG: TE Wegight

        # トリガーワード
        def modified_trigger_prompt(e):
            lora = self.sd["loras"][cmb_lora_name.get()]
            trigger_prompt = stx_trigger_prompt.get("1.0", tk.END)
            trigger_prompt = trigger_prompt.replace("\n\n\n", "").replace("\n\n", "").replace("\n", "")
            lora["trigger_prompt"] = trigger_prompt[: self.sd["lora_trigger_prompt_max_length"]]
            stx_trigger_prompt.edit_modified(False)
            self.ctx.stable_diffusion.lora_changed = True

        lbl_trigger_prompt = tk.Label(lora_editor, text=l10n["lora_editor_trigger_prompt"])
        lbl_trigger_prompt.pack(padx=padx, pady=pady, anchor="w")
        stx_trigger_prompt = scrolledtext.ScrolledText(lora_editor, height=3, undo=True, maxundo=-1)
        stx_trigger_prompt.configure({"spacing1": 4, "spacing2": 4, "spacing3": 4, "wrap": tk.WORD})
        stx_trigger_prompt.bind("<<Modified>>", modified_trigger_prompt)
        stx_trigger_prompt.pack(fill=tk.X, padx=padx, pady=pady)

        # オリジナルトリガーワード
        lbl_original_trigger_prompt = tk.Label(lora_editor, text=l10n["lora_editor_original_trigger_prompt"])
        lbl_original_trigger_prompt.pack(padx=padx, pady=pady, anchor="w")
        stx_original_trigger_prompt = scrolledtext.ScrolledText(lora_editor, state=tk.DISABLED)
        stx_original_trigger_prompt.configure({"spacing1": 4, "spacing2": 4, "spacing3": 4, "wrap": tk.WORD})
        stx_original_trigger_prompt.pack(expand=True, fill=tk.BOTH, padx=padx, pady=pady)

        select_lora(lora_name)
