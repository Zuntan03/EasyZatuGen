import json
import os
import tkinter as tk
from tkinter import filedialog

from path import Path
from serializer import Serializer


class FileMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx

        self.file_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["file_menu"], menu=self.file_menu)
        self.file_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        l10n = self.ctx.l10n
        self.file_menu.delete(0, "end")

        def open_file():
            file_path = filedialog.askopenfilename(
                initialdir=Path.get_output_dir(), filetypes=[("EasyZatuGen", "*.json; *.png")]
            )
            if file_path:
                self.ctx.open_file(file_path)

        self.file_menu.add_command(label=l10n["file_open"], command=open_file)

        def export_json():
            # path = os.path.join(Path.cwd, Path.get_output_path() + ".json")
            file_path = filedialog.asksaveasfilename(
                initialdir=Path.get_output_dir(),
                initialfile=Path.get_output_file_name(".json"),
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if file_path:
                json_data = json.dumps(Serializer.serialize(self.ctx), indent=4, ensure_ascii=False)
                with open(file_path, "w", encoding="utf-8-sig") as f:
                    f.write(json_data)
                print(json_data)

        self.file_menu.add_command(label=l10n["file_export"], command=export_json)

        self.file_menu.add_separator()

        self.file_menu.add_command(
            label=l10n["file_open_output_dir"], command=lambda: Path.open_dir(Path.get_output_dir())
        )

        self.file_menu.add_command(
            label=l10n["file_open_embedding_dir"], command=lambda: Path.open_dir(Path.embedding_dir)
        )

        self.file_menu.add_command(label=l10n["file_open_config_dir"], command=lambda: Path.open_dir(Path.config_dir))

        self.file_menu.add_separator()

        self.file_menu.add_command(label=l10n["file_reset_config"], command=lambda: self.ctx.reset_config())

        self.file_menu.add_separator()

        self.file_menu.add_command(label=l10n["file_exit"], command=self.ctx.finalize)
