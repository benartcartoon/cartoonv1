import os, subprocess, time
from PIL import Image
import gradio as gr

ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
MODEL=f"{ROOT}/models/Wan2.2-TI2V-5B"
OUT=f"{ROOT}/output"
INP=f"{ROOT}/input"
WAN="/content/Wan2.2"
os.makedirs(OUT, exist_ok=True); os.makedirs(INP, exist_ok=True)

def generate(image, prompt, frames, steps, seed):
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
            btn=gr.Button("VIDEO URET",variant="primary")
    video=gr.Video(label="Sonuc")
    status=gr.Textbox(label="Durum",lines=8)
    btn.click(generate,[image,prompt,frames,steps,seed],[video,status])

demo.queue().launch(share=True, show_error=True)
