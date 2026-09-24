from google.colab import drive
import os, subprocess, sys, shutil, time, urllib.request

drive.mount('/content/drive', force_remount=False)
BASE="/content/drive/MyDrive/MiniMax-H3"
COMFY=BASE+"/ComfyUI"
assert os.path.isdir(COMFY), "MiniMax-H3/ComfyUI Drive'da bulunamadi"

# GitHub'daki güncel otomasyon
subprocess.run(["bash","-lc","rm -rf /content/cartoonv1 && git clone -q --depth 1 https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1"],check=True)

# 40 sahnelik planı ilk kez Drive'a koy
ep=BASE+"/episodes/episode_001"
os.makedirs(ep,exist_ok=True)
if not os.path.exists(ep+"/plan.json"):
    shutil.copy2("/content/cartoonv1/episodes/episode_001.plan.json",ep+"/plan.json")

# Mevcut MiniMax ComfyUI bağımlılıkları; torch/cuda ailesine dokunma
req=COMFY+"/requirements.txt"; safe="/content/comfy_safe.txt"
with open(req,encoding="utf-8") as f: lines=f.readlines()
with open(safe,"w") as f:
    for line in lines:
        if not line.strip().lower().startswith(("torch","torchvision","torchaudio")): f.write(line)
subprocess.run([sys.executable,"-m","pip","install","-q","-r",safe],check=True)
subprocess.run([sys.executable,"-m","pip","install","-q","torchsde"],check=True)

# Gerekli MiniMax model dosyalarını doğrula
needed=[
 COMFY+"/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
 COMFY+"/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
 COMFY+"/models/vae/minimax_h3_audio_vae_fp32.safetensors",
]
missing=[p for p in needed if not os.path.exists(p)]
if missing: raise RuntimeError("MiniMax model dosyasi eksik: "+str(missing))

# ComfyUI API
log=open("/content/comfy_minimax.log","w")
p=subprocess.Popen([sys.executable,COMFY+"/main.py","--listen","127.0.0.1","--port","8188"],cwd=COMFY,stdout=log,stderr=subprocess.STDOUT)
for _ in range(180):
    try:
        urllib.request.urlopen("http://127.0.0.1:8188/system_stats",timeout=2); break
    except: time.sleep(2)
else:
    log.flush(); print(open("/content/comfy_minimax.log").read()[-8000:]); raise RuntimeError("ComfyUI baslamadi")

print("MINIMAX-H3 HAZIR. 10 dakikalik bolum basliyor.")
subprocess.run([sys.executable,"/content/cartoonv1/scripts/render_episode.py"],check=True)
