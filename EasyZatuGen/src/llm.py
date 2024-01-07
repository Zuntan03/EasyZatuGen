import gc
import time

import torch
from context import Context
from perf import Perf
from transformers import AutoModelForCausalLM, AutoTokenizer


class Llm:
    def __init__(self):
        self.model_name = ""
        self.model = None
        self.tokenizer = None

    def load_model(self, ctx):
        self.cfg = ctx.cfg.easy_zatu_gen
        start_time = Perf.start()
        self.model_name = self.cfg["model_name"]
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, device_map="auto", torch_dtype=torch.bfloat16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        Perf.end(start_time, f'Llm.load("{self.model_name}")')

    def generate(
        self, prompt, max_new_tokens=75, top_k=40, top_p=0.95, temperature=0.8, repetition_penalty=1.0, info=""
    ):
        start_time = Perf.start()
        input_ids, output_ids, text, num_tokens = None, None, "", 0
        try:
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.model.device)
            output_ids = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_k=top_k,
                top_p=top_p,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
            )
            text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            num_tokens = len(output_ids[0]) - len(input_ids[0])
        except RuntimeError as e:
            print(e)
        finally:
            del input_ids, output_ids
            torch.cuda.empty_cache()
        token_per_sec = num_tokens / (time.perf_counter() - start_time)
        Perf.end(start_time, f"Llm.generate({info}) {token_per_sec:.1f}t/s")
        if self.cfg["enable_llm_output_log"]:
            print_text = text.replace("\n\n\n", "\n").replace("\n\n", "\n").strip()
            print(Context.l10n["print_llm_output"].format(token_per_sec, print_text))
        return text
