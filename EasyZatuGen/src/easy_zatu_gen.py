import json
import time

import torch
from context import Context
from form import Form
from input_parser import InputParser
from job_queue import JobQueue
from llm import Llm
from path import Path
from perf import Perf
from PIL import Image, PngImagePlugin
from serializer import Serializer
from speech import Speech
from stable_diffusion import StableDiffusion


class EasyZatuGen:
    mainloop_sleep_time = 50
    vram_info_update_interval = 20

    def __init__(self):
        self.inittialzie_start = time.perf_counter()
        self.initialized = False

        Path.init()
        self.ctx = Context()
        Perf.ctx = self.ctx

        self.ctx.llm = Llm()
        self.ctx.speech = Speech()
        self.ctx.stable_diffusion = StableDiffusion()
        self.ctx.cpu_job_queue = JobQueue()
        self.ctx.gpu_job_queue = JobQueue()
        self.ctx.form = Form()
        self.ctx.parser = InputParser()

        self.ctx.gpu_job_queue.push(self.ctx.llm.load_model, ctx=self.ctx)

        form = self.ctx.form
        form.init_form(self.ctx)

        form.input_var.set(self.ctx.cfg.easy_zatu_gen["input"])
        self.ctx.parser.set_input(form.input_var)

        self.title = form.win.title()
        self.vram_info = ""
        self.total_vram = None
        self.reflesh_vram_info_counter = None

        form.win.protocol("WM_DELETE_WINDOW", self.ctx.finalize)
        form.win.dnd_bind("<<Drop>>", lambda e: self.ctx.open_file(e.data.strip()))
        form.win.after(EasyZatuGen.mainloop_sleep_time, self.mainloop)
        form.run()

    def mainloop(self):
        # start_time = time.perf_counter()

        self.ctx.parser.update(self.ctx)
        self.update_title()

        if self.ctx.stable_diffusion.mainloop(self.ctx):
            sd = self.ctx.stable_diffusion
            self.ctx.form.set_image(sd.image)

            png_path = Path.get_output_path(f"-{Path.get_path_name(sd.generated_prompt[:24])}.png")
            info = PngImagePlugin.PngInfo()
            info.add_itxt("ezzatugn", json.dumps(Serializer.serialize(self.ctx), indent=4, ensure_ascii=False))
            self.ctx.cpu_job_queue.push(lambda: sd.image.save(png_path, pnginfo=info))

            if not self.initialized:
                self.initialized = True
                print(self.ctx.l10n["print_initialized"].format(int(time.perf_counter() - self.inittialzie_start)))
        elif (not self.initialized) and (not self.ctx.cfg.stable_diffusion["enable"]):
            self.initialized = True
            print(self.ctx.l10n["print_initialized"].format(int(time.perf_counter() - self.inittialzie_start)))

        if self.initialized:
            self.ctx.speech.mainloop(self.ctx)

        self.ctx.cpu_job_queue.update()
        self.ctx.gpu_job_queue.update()
        self.ctx.form.win.after(EasyZatuGen.mainloop_sleep_time, self.mainloop)

        # if time.perf_counter() - start_time > 0.05:
        #     print(f"Long mainloop(): {time.perf_counter() - start_time:.2f}sec")

    def update_title(self):
        if self.initialized:
            if self.total_vram is None:
                if self.ctx.stable_diffusion.pipe is not None:
                    device = self.ctx.stable_diffusion.pipe.device
                    self.total_vram = torch.cuda.get_device_properties(device).total_memory
                    self.reflesh_vram_info_counter = 0
            else:
                if (self.reflesh_vram_info_counter == 0) and (self.ctx.stable_diffusion.pipe is not None):
                    # device = self.ctx.stable_diffusion.pipe.device
                    reserved_vram = torch.cuda.max_memory_reserved()
                    torch.cuda.reset_peak_memory_stats()
                    # BUG: タスクマネージャーと 2GB 程度のズレがでる
                    # self.vram_info = (
                    #     f"VRAM: {reserved_vram / (1024 ** 3):.1f}GB {reserved_vram * 100 // self.total_vram}%, "
                    # )

                self.reflesh_vram_info_counter += 1
                if self.reflesh_vram_info_counter >= EasyZatuGen.vram_info_update_interval:
                    self.reflesh_vram_info_counter = 0

        scale = self.ctx.cfg.stable_diffusion["upscale_scale"]
        width = int(self.ctx.cfg.stable_diffusion["width"] * scale)
        height = int(self.ctx.cfg.stable_diffusion["height"] * scale)
        size = f"{width}x{height}"

        main_char = self.ctx.parser.main_char
        if main_char == "":
            main_char = self.ctx.l10n["title_main_char_unset"]
        sp = self.ctx.cfg.speech
        title = self.ctx.l10n["title"].format(
            size,
            self.vram_info,
            self.ctx.cfg.stable_diffusion["model_name"],
            main_char,
            sp["main_char_voice"],
            sp["sub_char_voice"],
            sp["narrator_voice"],
        )
        if title != self.title:
            self.title = title
            self.ctx.form.win.title(title)


if __name__ == "__main__":
    easy_zatu_gen = EasyZatuGen()
