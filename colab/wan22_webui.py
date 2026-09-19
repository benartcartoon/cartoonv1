import os, subprocess, time
from PIL import Image
import gradio as gr

ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
MODEL=f"{ROOT}/models/Wan2.2-TI2V-5B"
OUT=f"{ROOT}/output"
INP=f"{ROOT}/input"
WAN="/content/Wan2.2"
os.makedirs(OUT, exist_ok=True); os.makedirs(INP, exist_ok=True)

def generate(image, prompt, frames, steps, seed, auto_audio, audio_prompt, progress=gr.Progress()):
    if image is None:
        return None, "Referans gorsel yukle."
    if not os.path.isfile(f"{MODEL}/config.json"):
        return None, f"Model bulunamadi: {MODEL}"
    stamp=time.strftime("%Y%m%d_%H%M%S")
    img=f"{INP}/reference_{stamp}.png"
    out=f"{OUT}/wan22_{stamp}.mp4"
    image.convert("RGB").save(img)
    # Stability-first prompt guard: reference identity and scene continuity take priority.
    stability_guard = """
STRICT STABILITY RULES: Preserve the exact identity, proportions, colors, face, eyes, accessories and materials of the reference character in every frame. Keep the background, lighting and camera consistent. Use one continuous shot with a mostly fixed camera. Perform only the clearly requested actions, one after another, with calm transitions. Do not invent additional actions or objects. Prioritize character consistency over dramatic motion. No morphing, no warping, no identity drift, no object duplication, no disappearing accessories, no extra limbs, no sudden pose jumps, no camera cuts, no zooms.
"""
    safe_prompt = prompt.strip() + "\n\n" + stability_guard.strip()
    cmd=[
        "python", f"{WAN}/generate.py",
        "--task","ti2v-5B","--size","1280*704",
        "--ckpt_dir",MODEL,
        "--image",img,
        "--prompt",safe_prompt,
        "--frame_num",str(int(frames)),
        "--sample_steps",str(int(steps)),
        "--base_seed",str(int(seed)),
        "--save_file",out
    ]
    progress(0.02, desc="WAN2.2 baslatiliyor / model yukleniyor...")
    p=subprocess.Popen(cmd,cwd=WAN,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1)
    logs=[]
    import re
    step_re=re.compile(r"(\\d+)\\s*/\\s*(\\d+)")
    for line in iter(p.stdout.readline, ""):
        logs.append(line)
        if len(logs) > 300:
            logs=logs[-300:]
        m=step_re.search(line)
        if m:
            cur,total=map(int,m.groups())
            if total > 0 and total <= 200:
                frac=min(0.92, 0.05 + 0.87*(cur/total))
                progress(frac, desc=f"Video uretiliyor: {cur}/{total} (%{int(cur*100/total)})")
    p.wait()
    if p.returncode != 0:
        return None, "URETIM HATASI:\n"+"".join(logs)[-6000:]
    progress(0.94, desc="Video tamamlandi; son islemler yapiliyor...")
    if auto_audio:
        progress(0.95, desc="AI ses uretiliyor...")
        try:
            import torch, soundfile as sf
            # AudioLDM2 uses GPT2 internals that changed in newer transformers.
            # Compatibility shim for current Colab transformers.
            from transformers import GPT2Model
            if not hasattr(GPT2Model, "_update_model_kwargs_for_generation"):
                def _update_model_kwargs_for_generation(self, outputs, model_kwargs, is_encoder_decoder=False, num_new_tokens=1):
                    if hasattr(outputs, "past_key_values") and outputs.past_key_values is not None:
                        model_kwargs["past_key_values"] = outputs.past_key_values
                    if "attention_mask" in model_kwargs and model_kwargs["attention_mask"] is not None:
                        am=model_kwargs["attention_mask"]
                        model_kwargs["attention_mask"]=torch.cat([am, am.new_ones((am.shape[0], num_new_tokens))], dim=-1)
                    return model_kwargs
                GPT2Model._update_model_kwargs_for_generation=_update_model_kwargs_for_generation
            from diffusers import AudioLDM2Pipeline
            duration=max(1.0, (int(frames)-1)/24.0)
            wav=f"{OUT}/wan22_{stamp}_audio.wav"
            final=f"{OUT}/wan22_{stamp}_sesli.mp4"
            pipe=AudioLDM2Pipeline.from_pretrained("cvssp/audioldm2", torch_dtype=torch.float16)
            pipe=pipe.to("cuda")
            audio=pipe(
                audio_prompt or "cute kitten meowing softly, playful cartoon ambience, clean sound effects",
                negative_prompt="distorted, noisy, harsh, speech, human voice",
                num_inference_steps=20,
                audio_length_in_s=duration
            ).audios[0]
            sf.write(wav, audio, 16000)
            del pipe
            torch.cuda.empty_cache()
            m=subprocess.run([
                "ffmpeg","-y","-i",out,"-i",wav,
                "-map","0:v:0","-map","1:a:0","-c:v","copy",
                "-c:a","aac","-b:a","192k","-shortest",final
            ],text=True,capture_output=True)
            if m.returncode == 0:
                progress(1.0, desc="Tamamlandi")
                return final, f"TAMAMLANDI (SESLI): {final}"
            return out, "Video tamamlandi; ses birlestirme basarisiz oldu. Sessiz video korundu."
        except Exception as e:
            return out, "Video tamamlandi; otomatik ses eklenemedi. Sessiz video korundu. SES HATASI: "+repr(e)
    progress(1.0, desc="Tamamlandi")
    return out, f"TAMAMLANDI: {out}"

with gr.Blocks(title="CartoonV1 WAN2.2") as demo:
    gr.Markdown("# CartoonV1 — WAN2.2 TI2V-5B\nReferans resmi yukle, promptu yaz ve VIDEO URET'e bas.")
    with gr.Row():
        image=gr.Image(type="pil",label="Karakter / ilk kare")
        with gr.Column():
            prompt=gr.Textbox(lines=6,label="Prompt",value="An adorable black cartoon kitten dances happily, with clear natural movement of arms, legs, head and body, consistent character identity, smooth cinematic 3D animation.")
            frames=gr.Slider(25,121,value=81,step=4,label="Kare sayisi (4n+1)")
            steps=gr.Slider(20,50,value=40,step=1,label="Steps")
            seed=gr.Number(value=3193264261,precision=0,label="Seed")
            auto_audio=gr.Checkbox(value=True,label="Otomatik AI ses ekle")
            audio_prompt=gr.Textbox(lines=2,label="Senkron ses tarifi",value="clean synchronized cartoon foley matching the visible actions, soft object handling sounds, movement whooshes only when movement happens, subtle room ambience, no music, no speech")
            btn=gr.Button("VIDEO URET",variant="primary")
    video=gr.Video(label="Sonuc")
    status=gr.Textbox(label="Durum",lines=8)
    btn.click(generate,[image,prompt,frames,steps,seed,auto_audio,audio_prompt],[video,status])

demo.queue().launch(share=True, show_error=True, allowed_paths=[OUT, INP])    if auto_audio:
        progress(0.95, desc="Video izleniyor ve hareketlere senkron ses uretiliyor...")
        try:
            import glob, shutil
            mma="/content/MMAudio"
            if not os.path.isfile(f"{mma}/demo.py"):
                raise RuntimeError("MMAudio kurulu degil. setup_wan22.sh ile kurulumu yenileyin.")
            duration=max(1.0, (int(frames)-1)/24.0)
            before=set(glob.glob(f"{mma}/output/*.mp4"))
            sfx_prompt=(audio_prompt.strip() if audio_prompt.strip() else
                "clean synchronized cartoon foley sound effects matching visible actions, no music, no speech")
            # Strongly suppress the failure mode we saw: unwanted music/voices.
            sfx_prompt += ". Foley and physical sound effects only. No background music. No melody. No singing. No speech."
            cmd_audio=[
                "python",f"{mma}/demo.py",
                f"--duration={duration:.3f}",
                f"--video={out}",
                "--prompt",sfx_prompt,
                "--negative_prompt","music, background music, melody, song, singing, human speech, dialogue, voice, noisy, distorted"
            ]
            a=subprocess.run(cmd_audio,cwd=mma,text=True,capture_output=True)
            if a.returncode != 0:
                raise RuntimeError((a.stderr or a.stdout)[-5000:])
            after=set(glob.glob(f"{mma}/output/*.mp4"))
            candidates=list(after-before) or glob.glob(f"{mma}/output/*.mp4")
            if not candidates:
                raise RuntimeError("MMAudio cikti videosu bulunamadi.")
            made=max(candidates,key=os.path.getmtime)
            final=f"{OUT}/wan22_{stamp}_senkron_sesli.mp4"
            shutil.copy2(made,final)
            progress(1.0, desc="Tamamlandi - senkron ses eklendi")
            return final, f"TAMAMLANDI (SENKRON SES): {final}"
        except Exception as e:
            return out, "Video tamamlandi; senkron ses eklenemedi. Sessiz video korundu. SES HATASI: "+repr(e)

