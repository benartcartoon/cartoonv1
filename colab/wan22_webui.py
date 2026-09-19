import os, subprocess, time
from PIL import Image
import gradio as gr

ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
MODEL=f"{ROOT}/models/Wan2.2-TI2V-5B"
OUT=f"{ROOT}/output"
INP=f"{ROOT}/input"
WAN="/content/Wan2.2"
os.makedirs(OUT, exist_ok=True); os.makedirs(INP, exist_ok=True)

def generate(image, prompt, frames, steps, seed, auto_audio, audio_prompt):
    if image is None:
        return None, "Referans gorsel yukle."
    if not os.path.isfile(f"{MODEL}/config.json"):
        return None, f"Model bulunamadi: {MODEL}"
    stamp=time.strftime("%Y%m%d_%H%M%S")
    img=f"{INP}/reference_{stamp}.png"
    out=f"{OUT}/wan22_{stamp}.mp4"
    image.convert("RGB").save(img)
    cmd=[
        "python", f"{WAN}/generate.py",
        "--task","ti2v-5B","--size","1280*704",
        "--ckpt_dir",MODEL,
        "--image",img,
        "--prompt",prompt,
        "--frame_num",str(int(frames)),
        "--sample_steps",str(int(steps)),
        "--base_seed",str(int(seed)),
        "--save_file",out
    ]
    p=subprocess.run(cmd,cwd=WAN,text=True,capture_output=True)
    if p.returncode != 0:
        return None, "URETIM HATASI:\n"+(p.stderr or p.stdout)[-6000:]
    if auto_audio:
        try:
            import torch, soundfile as sf
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
                return final, f"TAMAMLANDI (SESLI): {final}"
            return out, "Video tamamlandi; ses birlestirme basarisiz oldu. Sessiz video korundu."
        except Exception as e:
            return out, "Video tamamlandi; otomatik ses eklenemedi. Sessiz video korundu. SES HATASI: "+repr(e)
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
            audio_prompt=gr.Textbox(lines=2,label="Ses tarifi",value="cute orange kitten meowing happily while dancing, playful cartoon sound effects, soft paw movement sounds, gentle licking sound near the end, clean studio audio, no human speech")
            btn=gr.Button("VIDEO URET",variant="primary")
    video=gr.Video(label="Sonuc")
    status=gr.Textbox(label="Durum",lines=8)
    btn.click(generate,[image,prompt,frames,steps,seed,auto_audio,audio_prompt],[video,status])

demo.queue().launch(share=True, show_error=True, allowed_paths=[OUT, INP])
