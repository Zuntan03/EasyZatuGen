import copy
import gc
import glob
import logging
import os
import re
import warnings

# transformers\models\clip\feature_extraction_clip.py:28
warnings.simplefilter("ignore", FutureWarning, 28)

logger = logging.getLogger("xformers")
log_level = logger.level
logger.setLevel(logging.ERROR)
import torch
from context import Context
from diffusers import AutoencoderTiny
from job_queue import JobQueue
from lpw_stable_diffusion import StableDiffusionLongPromptWeightingPipeline
from path import Path
from perf import Perf
from PIL import Image
from streamdiffusion import StreamDiffusion
from streamdiffusion.image_utils import postprocess_image, process_image

logger.setLevel(log_level)


class StableDiffusion:
    num_inference_steps = 50
    eos_regex = re.compile(r'[,.!?"\']')

    def __init__(self):
        self.reset_generate_state(True)
        self.prompt_reset_count = None

        self.model_path = ""
        self.use_lcm = True
        self.lcm_weight = 1.0
        self.loras = []
        self.lora_changed = True

        self.pipe = None
        self.stream = None
        self.image = None

        self.translate_queue = JobQueue()
        self.translator = None

    def reset_generate_state(self, reset_prompt):
        if reset_prompt:
            self.llm_job = None
        self.args = None
        self.model_load_job = None
        self.generate_job = None
        self.upscale_job = None

    def mainloop(self, ctx):
        self.translate_queue.update()

        if not ctx.cfg.stable_diffusion["enable"]:
            return False

        if (self.llm_job is None) and (ctx.parser.theme != ""):
            self._generate_prompt(ctx)
        if (self.llm_job is None) or (not self.llm_job.successful()):
            return False

        if self.args is None:
            self._setup_args(ctx)

        if self.model_load_job is None:
            self.model_load_job = ctx.gpu_job_queue.push(self._load_model)
        if (self.model_load_job is None) or (not self.model_load_job.successful()):
            return False

        if self.generate_job is None:
            self.generate_job = ctx.gpu_job_queue.push(self._generate_iamge)
        if (self.generate_job is None) or (not self.generate_job.successful()):
            return False

        if self.args["upscale_enable"]:
            if self.upscale_job is None:
                self.upscale_job = ctx.gpu_job_queue.push(self._upscale_image)
            if (self.upscale_job is None) or (not self.upscale_job.successful()):
                return False

        if self.prompt_reset_count is None:
            self.prompt_reset_count = ctx.cfg.stable_diffusion["prompt_reset_count"]
        self.prompt_reset_count -= 1
        if (
            self.theme != ctx.parser.theme
            or self.main_char != ctx.parser.main_char
            or self.additional_prompt != ctx.parser.additional_prompt
            or self.prompt_reset_count <= 0
        ):
            self.reset_generate_state(True)
            self.prompt_reset_count = ctx.cfg.stable_diffusion["prompt_reset_count"]
        else:
            self.reset_generate_state(False)
        return True

    def _generate_prompt(self, ctx):
        self.theme = ctx.parser.theme
        self.main_char = ctx.parser.main_char
        if self.main_char == "":
            self.main_char = "人物"

        self.additional_prompt = ctx.parser.additional_prompt

        template = ""
        assert os.path.exists(Path.stable_diffusion_llm_template)
        with open(Path.stable_diffusion_llm_template, "r", encoding="utf-8-sig") as frsdt:
            template = frsdt.read()
        llm_prompt = template.format(theme=self.theme, main_char=self.main_char)
        cfg = ctx.cfg.stable_diffusion
        self.llm_job = ctx.gpu_job_queue.push(
            ctx.llm.generate,
            prompt=llm_prompt,
            max_new_tokens=cfg["max_new_tokens"],
            top_k=cfg["top_k"],
            top_p=cfg["top_p"],
            temperature=cfg["temperature"],
            repetition_penalty=cfg["repetition_penalty"],
            info="image_prompt",
        )

        def llm_callback(job):
            prompt = job.result[len(job.args["prompt"]) :].strip()
            eos_matches = list(StableDiffusion.eos_regex.finditer(prompt))
            if len(eos_matches) > 0:
                # print(prompt[eos_matches[-1].end() :])
                prompt = prompt[: eos_matches[-1].end()]
            prompt = prompt.replace("\n\n\n", "\n").replace("\n\n", "\n")
            self.generated_prompt = prompt

            if cfg["enable_image_prompt_log"]:
                print(Context.l10n["print_image_prompt"].format(prompt))

            if cfg["enable_translated_image_prompt_log"]:
                template = ""
                assert os.path.exists(Path.translate_llm_template)
                with open(Path.translate_llm_template, "r", encoding="utf-8-sig") as frtt:
                    template = frtt.read()
                llm_prompt = template.format(en_text=prompt)
                translate_job = ctx.gpu_job_queue.push(
                    ctx.llm.generate,
                    prompt=llm_prompt,
                    max_new_tokens=cfg["max_new_tokens"],
                    top_k=cfg["top_k"],
                    top_p=cfg["top_p"],
                    temperature=cfg["temperature"],
                    repetition_penalty=cfg["repetition_penalty"],
                    info="translate_image_prompt",
                )

                def translate_callback(job):
                    if ctx.cfg.easy_zatu_gen["enable_llm_output_log"]:
                        return
                    ja_txt = job.result[len(job.args["prompt"]) :].strip()
                    ja_txt = ja_txt.replace("\n\n\n", "\n").replace("\n\n", "\n")
                    print(Context.l10n["print_translated_image_prompt"].format(ja_txt))

                translate_job.callback = translate_callback

        self.llm_job.callback = llm_callback

    def _setup_args(self, ctx):
        sd = ctx.cfg.stable_diffusion
        loras = []
        for lora_name in list(sd["lora_names"]):
            if lora_name not in sd["loras"]:
                sd["lora_names"].remove(lora_name)
                continue
            lora_cfg = sd["loras"][lora_name]
            lora = {
                "name": lora_name,
                "path": lora_cfg["path"],
                "text_encoder_weight": lora_cfg["text_encoder_weight"],
                "unet_weight": lora_cfg["unet_weight"],
                "trigger_prompt": "",
            }
            if "trigger_prompt" in lora_cfg:
                lora["trigger_prompt"] = lora_cfg["trigger_prompt"]
            loras.append(lora)
            swap_lora = sd["loras"].pop(lora_name)
            sd["loras"][lora_name] = swap_lora

        additional_prompt = self.additional_prompt.strip()
        if not additional_prompt.endswith(","):
            additional_prompt += ","

        lora_prompt = ""
        for lora in loras:
            if lora["trigger_prompt"] != "":
                trigger_prompt = lora["trigger_prompt"].strip()
                trigger_prompt = trigger_prompt[: sd["lora_trigger_prompt_max_length"]].strip()
                lora_prompt += trigger_prompt
                if not lora["trigger_prompt"].endswith(","):
                    lora_prompt += ","
        self.prompt = additional_prompt + lora_prompt + self.generated_prompt
        self.prompt = self.prompt.replace("\n\n\n", "").replace("\n\n", "").replace("\n", "")
        self.disable_lora_prompt = additional_prompt + self.generated_prompt
        self.disable_lora_prompt = self.disable_lora_prompt.replace("\n\n\n", "").replace("\n\n", "").replace("\n", "")

        model_name = sd["model_name"]
        if model_name not in sd["models"]:
            model_name = list(sd["models"])[-1]
        model_path = sd["models"][model_name]["path"]
        swap_model = sd["models"].pop(model_name)
        sd["models"][model_name] = swap_model

        self.args = {
            "prompt": self.prompt,
            "disable_lora_prompt": self.disable_lora_prompt,
            "negative_prompt": sd["negative_prompt"],
            "model_name": model_name,
            "model_path": model_path,
            "use_lcm": sd["use_lcm"],
            "lcm_weight": sd["lcm_weight"],
            "loras": loras,
            "width": sd["width"],
            "height": sd["height"],
            "generate_t_index_list": copy.deepcopy(sd["generate_t_index_list"]),
            "upscale_enable": sd["upscale_enable"],
            "upscale_width": int(sd["upscale_scale"] * sd["width"]),
            "upscale_height": int(sd["upscale_scale"] * sd["height"]),
            "upscale_disable_lora": sd["upscale_disable_lora"],
            "upscale_t_index_list": copy.deepcopy(sd["upscale_t_index_list"]),
            "upscale_self_negative": sd["upscale_self_negative"],
            "upscale_guidance_scale": sd["upscale_guidance_scale"],
            "upscale_virtual_residual_noise_delta": sd["upscale_virtual_residual_noise_delta"],
            "embedding_dir": Path.embedding_dir,
        }

    def _load_model(self):
        args = self.args
        if (
            self.model_path == args["model_path"]
            and self.use_lcm == args["use_lcm"]
            and self.lcm_weight == args["lcm_weight"]
        ):
            if self.lora_changed or self.loras != args["loras"]:
                self._load_lora()
            return

        assert os.path.exists(args["model_path"])
        start_time = Perf.start()

        self.pipe = None
        self.stream = None
        self.clear_cache()

        # Hack: from_single_file() を維持しつつ、プロンプト最大長延長とプロンプト強調対応
        pipe = StableDiffusionLongPromptWeightingPipeline.from_single_file(args["model_path"])
        pipe.encode_prompt = lambda *args, **kwargs: (pipe._encode_prompt(*args, **kwargs), None)

        pipe = pipe.to(device=torch.device("cuda"), dtype=torch.bfloat16)

        for ti in glob.glob(os.path.join(args["embedding_dir"], "*.safetensors")):
            ti_name = os.path.splitext(os.path.basename(ti))[0]
            pipe.load_textual_inversion(ti, ti_name)

        for ti in glob.glob(os.path.join(args["embedding_dir"], "*.pt")):
            ti_name = os.path.splitext(os.path.basename(ti))[0]
            pipe.load_textual_inversion(ti, ti_name)

        stream = StreamDiffusion(
            pipe,
            t_index_list=args["generate_t_index_list"],
            torch_dtype=pipe.dtype,
            width=args["width"],
            height=args["height"],
            do_add_noise=True,
            use_denoising_batch=False,
            frame_buffer_size=1,
            cfg_type="none",
        )
        stream.vae = AutoencoderTiny.from_pretrained("madebyollin/taesd").to(device=pipe.device, dtype=pipe.dtype)

        if args["use_lcm"]:
            stream.load_lcm_lora()
            stream.fuse_lora(lora_scale=args["lcm_weight"])

        pipe.enable_xformers_memory_efficient_attention()

        self.pipe = pipe
        self.stream = stream
        self.model_path = args["model_path"]
        self.use_lcm = args["use_lcm"]
        self.lcm_weight = args["lcm_weight"]

        self._load_lora()

        Perf.end(start_time, f'StableDiffusion.load_model("{args["model_name"]}")')

    def _load_lora(self):
        start_time = Perf.start()
        self.pipe.unload_lora_weights()

        adapter_names = []
        adapter_text_encoder_weights = []
        adapter_unet_weights = []
        adapter_count = 0
        for lora in self.args["loras"]:
            adapter_name = f"adapter_{adapter_count}"
            adapter_count += 1
            try:
                self.pipe.load_lora_weights(".", weight_name=lora["path"], adapter_name=adapter_name)
                adapter_names.append(adapter_name)
                adapter_text_encoder_weights.append(lora["text_encoder_weight"])
                adapter_unet_weights.append(lora["unet_weight"])
            except Exception as e:
                print(e)
        # たぶんなんか間違ってる？
        # self.pipe.set_adapters_for_text_encoder(adapter_names, None, adapter_text_encoder_weights) # BUG: TE Wegight
        self.pipe.set_adapters(adapter_names, adapter_unet_weights)

        self.loras = self.args["loras"]
        self.lora_changed = False
        Perf.end(start_time, "StableDiffusion.load_lora()")

    def _generate_iamge(self):
        start_time = Perf.start()
        args = self.args
        self.reset_stream(args["generate_t_index_list"], args["width"], args["height"], "none", False)
        self.stream.prepare(
            args["prompt"],
            negative_prompt=args["negative_prompt"],
            delta=0,
            guidance_scale=1.0,
            num_inference_steps=StableDiffusion.num_inference_steps,
        )
        output = self.stream.txt2img()
        self.image = postprocess_image(output, output_type="pil")[0]
        del output
        self.free_stream()

        Perf.end(start_time, "StableDiffusion.generate_iamge()")

    def _upscale_image(self):
        start_time = Perf.start()
        args = self.args
        width = args["upscale_width"]
        height = args["upscale_height"]

        disable_lora = args["upscale_disable_lora"]
        if disable_lora:
            self.pipe.unload_lora_weights()
            self.clear_cache()

        image = self.image.resize((width, height), Image.Resampling.LANCZOS)
        input = process_image(image, (0, 1))[0]

        cfg_type = "none"
        if args["upscale_self_negative"]:
            cfg_type = "self"
        self.reset_stream(args["upscale_t_index_list"], width, height, cfg_type, True)

        self.stream.prepare(
            args["prompt"],  # 補助系のプロンプトが生きるので残したほうがいいかも？
            # args["disable_lora_prompt"] if disable_lora else args["prompt"],
            negative_prompt=args["negative_prompt"],
            delta=args["upscale_virtual_residual_noise_delta"],
            guidance_scale=args["upscale_guidance_scale"],
            num_inference_steps=StableDiffusion.num_inference_steps,
        )

        for _ in range(self.stream.batch_size - 1):
            self.stream(input)
        output = self.stream(input)
        self.image = postprocess_image(output, output_type="pil")[0]

        del image, input, output
        self.free_stream()

        if disable_lora:
            self._load_lora()

        Perf.end(start_time, "StableDiffusion.upscale_image()")

    def reset_stream(self, t_index_list, width, height, cfg_type, use_denoising_batch):
        stream = self.stream
        stream.t_list = t_index_list

        stream.width = width
        stream.height = height
        stream.latent_width = int(width // stream.pipe.vae_scale_factor)
        stream.latent_height = int(height // stream.pipe.vae_scale_factor)

        stream.use_denoising_batch = use_denoising_batch
        stream.cfg_type = cfg_type

        stream.denoising_steps_num = len(stream.t_list)

        assert cfg_type in ["none", "self"]
        if stream.use_denoising_batch:
            stream.batch_size = stream.denoising_steps_num * stream.frame_bff_size
            stream.trt_unet_batch_size = stream.denoising_steps_num * stream.frame_bff_size
        else:
            stream.batch_size = stream.frame_bff_size
            stream.trt_unet_batch_size = stream.frame_bff_size

    def free_stream(self):
        stream = self.stream
        del stream.x_t_latent_buffer
        del stream.prompt_embeds
        del stream.sub_timesteps_tensor
        del stream.init_noise
        del stream.stock_noise
        del stream.alpha_prod_t_sqrt
        del stream.beta_prod_t_sqrt

        self.clear_cache()

    def clear_cache(self):
        gc.collect()
        torch.cuda.empty_cache()
