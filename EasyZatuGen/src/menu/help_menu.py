import tkinter as tk
import webbrowser

from path import Path


class HelpMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx
        ezg = ctx.cfg.easy_zatu_gen

        self.help_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=ctx.l10n["help_menu"], menu=self.help_menu)
        self.help_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.help_menu.delete(0, "end")
        l10n = self.ctx.l10n

        def open_url(url):
            webbrowser.open(url, new=1)

        self.help_menu.add_command(
            label=l10n["help_how_to_use"],
            command=lambda: open_url(
                r"https://github.com/Zuntan03/EasyZatuGen?tab=readme-ov-file#%E4%BD%BF%E3%81%84%E3%81%8B%E3%81%9F"
            ),
        )

        self.help_menu.add_separator()

        reference_menu = tk.Menu(self.help_menu, tearoff=False)
        self.help_menu.add_cascade(label=l10n["help_reference"], menu=reference_menu)

        reference_menu.add_command(
            label="casper-hansen/AutoAWQ",
            command=lambda: open_url("https://github.com/casper-hansen/AutoAWQ/"),
        )

        reference_menu.add_command(
            label="litagin02/Style-Bert-VITS2",
            command=lambda: open_url("https://github.com/litagin02/Style-Bert-VITS2/"),
        )

        reference_menu.add_command(
            label="cumulo-autumn/StreamDiffusion",
            command=lambda: open_url("https://github.com/cumulo-autumn/StreamDiffusion/"),
        )

        self.help_menu.add_separator()

        self.help_menu.add_command(
            label=l10n["help_easy_zatu_gen"],
            command=lambda: open_url("https://github.com/Zuntan03/EasyZatuGen"),
        )
