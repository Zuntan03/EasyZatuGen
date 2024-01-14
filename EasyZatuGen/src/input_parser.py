import re

import pyperclip


class InputParser:
    def __init__(self):
        self.input_var = None
        self.parsed_var = None
        self.theme = ""
        self.main_char = ""
        self.additional_prompt = ""
        self.main_regex_h = re.compile(r"\{.*?\}")
        self.main_regex_f = re.compile(r"｛.*?｝")

        self.pre_clipboard = None
        self.theme_var = None
        self.prompt_var = None

    def set_input(self, input_var):
        self.input_var = input_var

    def update(self, ctx):
        if self.input_var is None:
            return

        if ctx.cfg.easy_zatu_gen["clipboard_linkage"] and (self.theme_var is not None):
            if self.pre_clipboard is None:
                self.pre_clipboard = pyperclip.paste()
            else:
                try:
                    clipboard = pyperclip.paste()
                    if clipboard != self.pre_clipboard:
                        if self.set_clipboard(clipboard, ctx, self.theme_var, self.prompt_var):
                            self.pre_clipboard = clipboard
                except Exception as e:
                    print(e)
        elif self.pre_clipboard is not None:
            self.pre_clipboard = None

        input_var = self.input_var.get()
        if input_var == self.parsed_var:
            return
        self.parsed_var = input_var

        self.additional_prompt = ""
        pipe_split = input_var.split("|", 1)
        if len(pipe_split) == 2:
            input_var = pipe_split[0]
            self.additional_prompt = pipe_split[1]
        else:
            pipe_split = input_var.split("｜", 1)
            if len(pipe_split) == 2:
                input_var = pipe_split[0]
                self.additional_prompt = pipe_split[1]

        self.theme_var = input_var
        self.prompt_var = self.additional_prompt

        self.main_char = ""
        match_main_h = self.main_regex_h.search(input_var)
        if match_main_h:
            self.main_char = match_main_h.group()[1:-1]
            input_var = self.main_regex_h.sub(self.main_char, input_var, count=1)
        else:
            match_main_f = self.main_regex_f.search(input_var)
            if match_main_f:
                self.main_char = match_main_f.group()[1:-1]
                input_var = self.main_regex_f.sub(self.main_char, input_var, count=1)
        self.theme = input_var

    def set_clipboard(self, text, ctx, theme_var, prompt_var):
        if not ((text.count("|") == 1) or (text.count("｜") == 1)):
            return False

        text = text.replace("\n\n\n", "").replace("\n\n", "").replace("\n", "").strip()

        pipe_split = text.split("|", 1)
        left, right = "", ""
        if len(pipe_split) == 2:
            left = pipe_split[0].strip()
            right = pipe_split[1].strip()
        else:
            pipe_split = text.split("｜", 1)
            left = pipe_split[0].strip()
            right = pipe_split[1].strip()
        if (left == "") and (right == ""):
            return False
        theme_var = theme_var if left == "" else left
        prompt_var = prompt_var if right == "" else right
        ctx.form.input_var.set(f"{theme_var}|{prompt_var}")
        return True
