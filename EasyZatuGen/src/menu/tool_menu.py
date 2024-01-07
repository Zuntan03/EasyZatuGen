import tkinter as tk

from path import Path


class ToolMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx

        self.tool_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["tool_menu"], menu=self.tool_menu)
        self.tool_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.tool_menu.delete(0, "end")

        ezg = self.ctx.cfg.easy_zatu_gen
        l10n = self.ctx.l10n

        # クリップボード連携
        def clipboard_linkage():
            ezg["clipboard_linkage"] = self.clipboard_linkage_var.get()

        self.clipboard_linkage_var = tk.BooleanVar()
        self.clipboard_linkage_var.set(ezg["clipboard_linkage"])
        self.tool_menu.add_checkbutton(
            label=l10n["tool_clipboard_linkage"],
            variable=self.clipboard_linkage_var,
            command=clipboard_linkage,
        )

        # TODO: 動画作成？
