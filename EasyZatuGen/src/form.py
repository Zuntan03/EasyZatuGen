import tkinter as tk

from context import Context
from menu.file_menu import FileMenu
from menu.help_menu import HelpMenu
from menu.image_menu import ImageMenu
from menu.log_menu import LogMenu
from menu.lora_menu import LoraMenu
from menu.model_menu import ModelMenu
from menu.sample_menu import SampleMenu
from menu.speech_menu import SpeechMenu
from menu.tool_menu import ToolMenu
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD


class Form:
    win_min_w = 440
    win_min_h = 100

    def __init__(self):
        pass

    def init_form(self, ctx):
        self.win = TkinterDnD.Tk()
        self.win.drop_target_register(DND_FILES)
        self.win.title("EasyZatuGen")
        self.win.minsize(Form.win_min_w, Form.win_min_h)
        cfg = ctx.cfg.easy_zatu_gen
        l10n = Context.l10n

        win_geom = f'{cfg["win_width"]}x{cfg["win_height"]}'
        if cfg["win_x"] != 0 or cfg["win_y"] != 0:
            win_geom += f'+{cfg["win_x"]}+{cfg["win_y"]}'
        self.win.geometry(win_geom)

        self.menu_bar = tk.Menu(self.win)
        self.win.config(menu=self.menu_bar)

        self.file_menu = FileMenu(self, ctx)
        self.image_menu = ImageMenu(self, ctx)
        self.model_menu = ModelMenu(self, ctx)
        self.lora_menu = LoraMenu(self, ctx)
        self.speech_menu = SpeechMenu(self, ctx)
        self.log_menu = LogMenu(self, ctx)
        self.tool_menu = ToolMenu(self, ctx)
        self.sample_menu = SampleMenu(self, ctx)
        self.help_menu = HelpMenu(self, ctx)

        self.win.config(menu=None)
        self.win.config(menu=self.menu_bar)

        self.input_var = tk.StringVar()

        self.input = tk.Entry(
            self.win,
            textvariable=self.input_var,
            font=(None, cfg["input_font_size"]),
            fg=cfg["fg"],
            bg=cfg["bg"],
            selectforeground=cfg["select_fg"],
            selectbackground=cfg["select_bg"],
            insertbackground=cfg["select_fg"],
        )
        self.input.pack(fill=tk.X, padx=1, pady=1)

        self.image = Image.new("RGB", (16, 16), "#000000")
        self.photo = ImageTk.PhotoImage(self.image)

        self.img_pane = tk.Label(self.win, image=self.photo, background=cfg["bg"])
        self.img_pane.pack(expand=True, fill="both")
        self.win.bind("<Configure>", self.resize)

    def resize(self, event):
        self.img_pane_width = event.width
        self.img_pane_height = event.height
        self.set_image(self.image)

    def run(self):
        self.win.lift()
        self.win.mainloop()

    def save_config(self, ctx):
        cfg = ctx.cfg.easy_zatu_gen
        cfg["win_width"] = self.win.winfo_width()
        cfg["win_height"] = self.win.winfo_height()
        cfg["win_x"] = self.win.winfo_x()
        cfg["win_y"] = self.win.winfo_y()

    def set_image(self, image):
        self.image = image
        scale = min(self.img_pane_width / image.width, self.img_pane_height / image.height)
        image_w = int(image.width * scale)
        image_h = int(image.height * scale)

        resized_image = self.image.resize((image_w, image_h), Image.Resampling.BILINEAR)
        self.photo = ImageTk.PhotoImage(resized_image)
        self.img_pane.config(image=self.photo)
