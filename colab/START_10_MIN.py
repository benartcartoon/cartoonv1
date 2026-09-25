from google.colab import drive, output
import os, subprocess, sys, time, urllib.request

drive.mount('/content/drive', force_remount=False)

BASE="/content/drive/MyDrive/MiniMax-H3"
COMFY=BASE+"/ComfyUI"
assert os.path.isfile(COMFY+"/main.py"), "ComfyUI bulunamadi: "+COMFY

print("1/4 ComfyUI bagimliliklari kontrol ediliyor...")

# Colab'in mevcut Torch/CUDA kurulumuna dokunma.
req=COMFY+"/requirements.txt"
safe="/content/comfy_requirements_safe.txt"
skip=("torch","torchvision","torchaudio")
with open(req,encoding="utf-8") as src, open(safe,"w",encoding="utf-8") as dst:
    for line in src:
        s=line.strip().lower()
        if not s or s.startswith("#"):
            dst.write(line); continue
        pkg=s.split(";",1)[0].strip()
        if any(pkg.startswith(x) for x in skip):
            continue
        dst.write(line)

subprocess.run([sys.executable,"-m","pip","install","-q","-r",safe],check=True)
# Onceki kurulumlarda eksik kalan temel paketleri de garanti et.
subprocess.run([sys.executable,"-m","pip","install","-q","alembic","blake3","torchsde"],check=True)
print("OK - bagimliliklar hazir")

print("2/4 MiniMax model dosyalari kontrol ediliyor...")
needed=[
 COMFY+"/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
 COMFY+"/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
 COMFY+"/models/vae/minimax_h3_audio_vae_fp32.safetensors",
]
missing=[p for p in needed if not os.path.exists(p)]
if missing:
    raise RuntimeError("MiniMax icin gerekli model dosyalari eksik:\n" + "\n".join(missing))

# Video VAE farkli ComfyUI kurulumlarinda opsiyonel olabilir; varsa kullanilir.
video_vae=COMFY+"/models/vae/minimax_h3_video_vae_int8_convrot.safetensors"
if os.path.exists(video_vae):
    print("OK - MiniMax modelleri hazir")
else:
    print("NOT - video VAE dosyasi bu kurulumda yok; ComfyUI yine acilacak.")

print("3/4 ComfyUI baslatiliyor...")

def alive():
    try:
        return urllib.request.urlopen("http://127.0.0.1:8188/system_stats",timeout=2).status == 200
    except Exception:
        return False

if not alive():
    # Onceki yarim kalmis surecleri temizle.
    subprocess.run(["bash","-lc","pkill -f '/MiniMax-H3/ComfyUI/main.py' 2>/dev/null || true"],check=False)
    time.sleep(1)
    log=open("/content/comfy_minimax.log","w")
    p=subprocess.Popen(
        [sys.executable,"-u",COMFY+"/main.py","--listen","127.0.0.1","--port","8188"],
        cwd=COMFY,stdout=log,stderr=subprocess.STDOUT
    )
    # Drive uzerinden ilk acilis A100'de bile uzun surebilir.
    # Sabit timeout ile saglikli sureci yanlislikla hata sayma.
    waited=0
    while not alive():
        if p.poll() is not None:
            log.flush()
            tail=open("/content/comfy_minimax.log",errors="ignore").read()[-12000:]
            print(tail)
            raise RuntimeError("ComfyUI sureci kapandi; yukaridaki log son hatayi gosteriyor.")
        time.sleep(5)
        waited += 5
        if waited % 60 == 0:
            print(f"ComfyUI yukleniyor... {waited//60} dk")

print("OK - ComfyUI calisiyor")
print("4/4 Arayuz aciliyor...")
print("Drive:",BASE)
output.serve_kernel_port_as_iframe(8188,height=1000)
