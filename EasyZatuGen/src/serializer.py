import json
import os
import webbrowser
from tkinter import messagebox

from path import Path


class Serializer:
    @classmethod
    def serialize(cls, ctx):
        data = {}

        easy_zatu_gen = {"input": ctx.form.input_var.get()}
        data["easy_zatu_gen"] = easy_zatu_gen

        sp = ctx.cfg.speech
        speech = {
            "play_interval": sp["play_interval"],
            "max_new_tokens": sp["max_new_tokens"],
            "auto_split": sp["auto_split"],
            "main_char_voice": sp["main_char_voice"],
            "main_char_style": sp["main_char_style"],
            "main_char_style_weight": sp["main_char_style_weight"],
            "sub_char_voice": sp["sub_char_voice"],
            "sub_char_style": sp["sub_char_style"],
            "sub_char_style_weight": sp["sub_char_style_weight"],
            "narrator_voice": sp["narrator_voice"],
            "narrator_style": sp["narrator_style"],
            "narrator_style_weight": sp["narrator_style_weight"],
        }
        data["speech"] = speech

        sd = ctx.cfg.stable_diffusion
        stable_diffusion = {
            "negative_prompt": sd["negative_prompt"],
            "model_name": sd["model_name"],
            "use_lcm": sd["use_lcm"],
            "lora_names": sd["lora_names"],
            "upscale_disable_lora": sd["upscale_disable_lora"],
            "upscale_self_negative": sd["upscale_self_negative"],
            "models": {},
            "loras": {},
        }
        model = sd["models"][sd["model_name"]].copy()
        del model["path"]
        stable_diffusion["models"] = {sd["model_name"]: model}

        for lora_name in sd["lora_names"]:
            lora = sd["loras"][lora_name].copy()
            del lora["path"]
            stable_diffusion["loras"][lora_name] = lora
        data["stable_diffusion"] = stable_diffusion

        return data

    @classmethod
    def deserialize(cls, ctx, data):
        l10n = ctx.l10n
        if "easy_zatu_gen" in data:
            easy_zatu_gen = data["easy_zatu_gen"]
            if "input" in easy_zatu_gen:
                ctx.form.input_var.set(easy_zatu_gen["input"])

        sp = ctx.cfg.speech
        if "speech" in data:
            speech = data["speech"]
            if "play_interval" in speech:
                sp["play_interval"] = speech["play_interval"]
            if "max_new_tokens" in speech:
                sp["max_new_tokens"] = speech["max_new_tokens"]
            if "auto_split" in speech:
                sp["auto_split"] = speech["auto_split"]

            if "main_char_voice" in speech:
                sp["main_char_voice"] = speech["main_char_voice"]
            if "main_char_style" in speech:
                sp["main_char_style"] = speech["main_char_style"]
            if "main_char_style_weight" in speech:
                sp["main_char_style_weight"] = speech["main_char_style_weight"]

            if "sub_char_voice" in speech:
                sp["sub_char_voice"] = speech["sub_char_voice"]
            if "sub_char_style" in speech:
                sp["sub_char_style"] = speech["sub_char_style"]
            if "sub_char_style_weight" in speech:
                sp["sub_char_style_weight"] = speech["sub_char_style_weight"]

            if "narrator_voice" in speech:
                sp["narrator_voice"] = speech["narrator_voice"]
            if "narrator_style" in speech:
                sp["narrator_style"] = speech["narrator_style"]
            if "narrator_style_weight" in speech:
                sp["narrator_style_weight"] = speech["narrator_style_weight"]

        sd = ctx.cfg.stable_diffusion
        if "stable_diffusion" in data:
            stable_diffusion = data["stable_diffusion"]
            if "negative_prompt" in stable_diffusion:
                sd["negative_prompt"] = stable_diffusion["negative_prompt"]
                if not sd["negative_prompt"] in sd["negative_prompts"]:  # 未知のNg足す
                    sd["negative_prompts"].append(sd["negative_prompt"])
                    msg = l10n["dlg_unkonwn_negative"].format(sd["negative_prompt"])
                    messagebox.showinfo(None, msg)
                    print(msg)
            if "model_name" in stable_diffusion:
                model_name = stable_diffusion["model_name"]
                if model_name in sd["models"]:
                    sd["model_name"] = model_name
                else:
                    model = stable_diffusion["models"][model_name]
                    if "download_url" in model:
                        model["path"] = os.path.join(Path.model_dir, model_name + ".safetensors")
                        messagebox.askyesno(None, l10n["dlg_download"].format(model["download_url"], model["path"]))
                        cmd = f'curl -Lo {model["path"]} {model["download_url"]}'
                        if "information_url" in model:
                            webbrowser.open(model["information_url"], new=1)
                        result = os.system(cmd)
                        if result == 0:
                            sd["models"][model_name] = model
                            sd["model_name"] = model_name
                        else:
                            msg = l10n["dlg_download_failed"].format(model["download_url"])
                            messagebox.showinfo(None, msg)
                            print(msg)
                    else:
                        msg = l10n["dlg_unkonwn_model"].format(model_name)
                        messagebox.showinfo(None, msg)
                        print(msg)
            if "use_lcm" in stable_diffusion:
                sd["use_lcm"] = stable_diffusion["use_lcm"]
            if "lora_names" in stable_diffusion:
                lora_names = stable_diffusion["lora_names"]
                sd["lora_names"] = []  # lora_names に指定があればそれに従う
                for lora_name in lora_names:
                    if lora_name in sd["loras"]:
                        sd["lora_names"].append(lora_name)
                    else:
                        lora = stable_diffusion["loras"][lora_name]
                        if "download_url" in lora:
                            lora["path"] = os.path.join(Path.lora_dir, lora_name + ".safetensors")
                            messagebox.askyesno(None, l10n["dlg_download"].format(lora["download_url"], lora["path"]))
                            cmd = f'curl -Lo {lora["path"]} {lora["download_url"]}'
                            if "information_url" in lora:
                                webbrowser.open(lora["information_url"], new=1)
                            result = os.system(cmd)
                            if result == 0:
                                sd["loras"][lora_name] = lora
                                sd["lora_names"].append(lora_name)
                            else:
                                msg = l10n["dlg_download_failed"].format(lora["download_url"])
                                messagebox.showinfo(None, msg)
                                print(msg)
            if "upscale_disable_lora" in stable_diffusion:
                sd["upscale_disable_lora"] = stable_diffusion["upscale_disable_lora"]
            if "upscale_self_negative" in stable_diffusion:
                sd["upscale_self_negative"] = stable_diffusion["upscale_self_negative"]
            if "loras" in stable_diffusion:
                for lora_name in stable_diffusion["loras"]:
                    src_lora = stable_diffusion["loras"][lora_name]
                    if lora_name in sd["loras"]:
                        dst_lora = sd["loras"][lora_name]
                        if "text_encoder_weight" in src_lora:
                            dst_lora["text_encoder_weight"] = src_lora["text_encoder_weight"]
                        if "unet_weight" in src_lora:
                            dst_lora["unet_weight"] = src_lora["unet_weight"]
                        if "trigger_prompt" in src_lora and src_lora["trigger_prompt"] != "":
                            dst_lora["trigger_prompt"] = src_lora["trigger_prompt"]
