import tkinter as tk

from path import Path


class ImageMenu:
    def __init__(self, form, ctx):
        self.form = form
        self.ctx = ctx
        cfg = ctx.cfg.stable_diffusion
        l10n = ctx.l10n

        self.image_menu = tk.Menu(form.menu_bar, tearoff=False)
        form.menu_bar.add_cascade(label=l10n["image_menu"], menu=self.image_menu)
        self.image_menu.configure(postcommand=self.on_menu_open)

    def on_menu_open(self):
        self.image_menu.delete(0, "end")
        cfg = self.ctx.cfg.stable_diffusion
        l10n = self.ctx.l10n

        # 画像を生成する
        def set_enable(*args):
            cfg["enable"] = enable_var.get()

        enable_var = tk.BooleanVar(value=cfg["enable"])
        enable_var.trace_add("write", set_enable)
        self.image_menu.add_checkbutton(label=l10n["image_enable"], variable=enable_var)

        # 画像プロンプト変更までの生成枚数
        def set_image_prompt_reset_count(count):
            cfg["prompt_reset_count"] = count
            self.image_menu.entryconfigure(0, label=l10n["image_prompt_reset_count"].format(count))

        prompt_reset_count_menu = tk.Menu(self.image_menu, tearoff=False)
        self.image_menu.add_cascade(
            label=l10n["image_prompt_reset_count"].format(cfg["prompt_reset_count"]), menu=prompt_reset_count_menu
        )

        for count in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            prompt_reset_count_menu.add_command(
                label=f"{count}", command=lambda count=count: set_image_prompt_reset_count(count)
            )

        # 幅
        width_menu = tk.Menu(self.image_menu, tearoff=False)
        self.image_menu.add_cascade(label=l10n["image_width"].format(cfg["width"]), menu=width_menu)

        def set_width(width):
            cfg["width"] = width
            self.image_menu.entryconfigure(1, label=l10n["image_width"].format(width))

        size = [384, 512, 640, 768, 896, 1024, 1152, 1280, 1408, 1536, 1664, 1792, 1920, 2048]
        for w in size:
            width_menu.add_command(label=f"{w}px", command=lambda w=w: set_width(w))

        # 高さ
        height_menu = tk.Menu(self.image_menu, tearoff=False)
        self.image_menu.add_cascade(label=l10n["image_height"].format(cfg["height"]), menu=height_menu)

        def set_height(height):
            cfg["height"] = height
            self.image_menu.entryconfigure(2, label=l10n["image_height"].format(height))

        for h in size:
            height_menu.add_command(label=f"{h}px", command=lambda h=h: set_height(h))

        # 幅と高さを入れ替え
        def swap_width_height():
            cfg["width"], cfg["height"] = cfg["height"], cfg["width"]
            self.image_menu.entryconfigure(1, label=l10n["image_width"].format(cfg["width"]))
            self.image_menu.entryconfigure(2, label=l10n["image_height"].format(cfg["height"]))

        self.image_menu.add_command(label=l10n["image_swap_width_height"], command=swap_width_height)

        # ネガティブプロンプト
        negative_prompt_menu = tk.Menu(self.image_menu, tearoff=False)
        self.image_menu.add_cascade(
            label=l10n["image_negative_prompt"].format(cfg["negative_prompt"]), menu=negative_prompt_menu
        )

        def set_negative_prompt(negative_prompt):
            cfg["negative_prompt"] = negative_prompt
            self.image_menu.entryconfigure(4, label=l10n["image_negative_prompt"].format(negative_prompt))

        for negative_prompt in cfg["negative_prompts"]:
            negative_prompt_menu.add_command(
                label=negative_prompt, command=lambda np=negative_prompt: set_negative_prompt(np)
            )

        self.image_menu.add_separator()

        # アップスケール
        def set_upscale_enable(*args):
            cfg["upscale_enable"] = upscale_enable_var.get()

        upscale_enable_var = tk.BooleanVar(value=cfg["upscale_enable"])
        upscale_enable_var.trace_add("write", set_upscale_enable)
        self.image_menu.add_checkbutton(label=l10n["image_upscale_enable"], variable=upscale_enable_var)

        # アップスケール倍率
        upscale_scale_menu = tk.Menu(self.image_menu, tearoff=False)
        self.image_menu.add_cascade(
            label=l10n["image_upscale_scale"].format(cfg["upscale_scale"]), menu=upscale_scale_menu
        )

        def set_upscale_scale(upscale_scale):
            cfg["upscale_scale"] = upscale_scale
            self.image_menu.entryconfigure(7, label=l10n["image_upscale_scale"].format(upscale_scale))

        upscale_scale = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4]
        for scale in upscale_scale:
            upscale_scale_menu.add_command(label=f"x{scale}", command=lambda scale=scale: set_upscale_scale(scale))

        # アップスケールで LoRA を無効化する
        def set_upscale_disable_lora(*args):
            cfg["upscale_disable_lora"] = upscale_disable_lora_var.get()

        upscale_disable_lora_var = tk.BooleanVar(value=cfg["upscale_disable_lora"])
        upscale_disable_lora_var.trace_add("write", set_upscale_disable_lora)
        self.image_menu.add_checkbutton(label=l10n["image_upscale_disable_lora"], variable=upscale_disable_lora_var)

        self.image_menu.add_separator()

        # LCM を使う
        def set_use_lcm(*args):
            cfg["use_lcm"] = use_lcm_var.get()

        use_lcm_var = tk.BooleanVar(value=cfg["use_lcm"])
        use_lcm_var.trace_add("write", set_use_lcm)
        self.image_menu.add_checkbutton(label=l10n["image_lcm_enable"], variable=use_lcm_var)

        # セルフネガティブを使う
        def set_upscale_self_negative(*args):
            cfg["upscale_self_negative"] = upscale_self_negative_var.get()

        upscale_self_negative_var = tk.BooleanVar(value=cfg["upscale_self_negative"])
        upscale_self_negative_var.trace_add("write", set_upscale_self_negative)
        self.image_menu.add_checkbutton(label=l10n["image_upscale_self_negative"], variable=upscale_self_negative_var)


#    "upscale_self_negative": false,
#    "image_upscale_self_negative": "セルフネガティブを使う",
