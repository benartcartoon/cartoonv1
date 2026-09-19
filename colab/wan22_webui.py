import os, subprocess, shlex, time
import gradio as gr
ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
MODEL=f"{ROOT}/models/Wan2.2-TI2V-5B"
OUT=f"{ROOT}/output"
WAN="/content/Wan2.2"
os.makedirs(OUT,exist_ok=True)

def generate(image,prompt,frames,steps,seed):
    if image is None: return None,"Referans görsel yükle."
    if not os.path.isdir(MODEL): return None,f"Model bulunamadı: {MODEL}"
    img=f"{ROOT}/input/reference.png"; image.save(img)
    before=set(os.listdir(OUT))
    cmd=["python",f"{WAN}/generate.py","--task","ti2v-5B","--size","1280*704","--ckpt_dir",MODEL,
         "--image",img,"--prompt",prompt,"--frame_num",str(int(frames)),"--sample_steps",str(int(steps)),
         "--seed",str(int(seed)),"--save_file",f"{OUT}/wan22_test.mp4"]
    p=subprocess.run(cmd,cwd=WAN,text=True,capture_output=True)
    video=f"{OUT}/wan22_test.mp4"
    if p.returncode!=0: return None,p.stderr[-5000:]
    return video,"TAMAMLANDI — video Drive/output içine kaydedildi."

with gr.Blocks(title="CartoonV1 WAN2.2") as demo:
    gr.Markdown("# CartoonV1 — WAN2.2 TI2V-5B")
    with gr.Row():
        image=gr.Image(type="pil",label="Karakter / ilk kare")
        with gr.Column():
            prompt=gr.Textbox(lines=7,label="Prompt",value="An adorable black cartoon kitten dances happily, clearly moving its arms, legs, head and body, smooth natural motion, consistent character identity, cinematic 3D animation.")
            frames=gr.Slider(25,121,value=81,step=4,label="Kare sayısı (24 FPS)")
            steps=gr.Slider(20,50,value=40,step=1,label="Steps")
            seed=gr.Number(value=3193264261,precision=0,label="Seed")
            btn=gr.Button("VIDEO ÜRET",variant="primary")
    video=gr.Video(label="Sonuç")
    status=gr.Textbox(label="Durum")
    btn.click(generate,[image,prompt,frames,steps,seed],[video,status])
demo.queue().launch(share=True,debug=True)
