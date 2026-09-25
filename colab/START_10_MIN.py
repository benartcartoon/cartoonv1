from google.colab import drive, output
import os, subprocess, sys, time, urllib.request

drive.mount('/content/drive', force_remount=False)

BASE="/content/drive/MyDrive/MiniMax-H3"
COMFY=BASE+"/ComfyUI"
assert os.path.isfile(COMFY+"/main.py"), "ComfyUI bulunamadi: "+COMFY

# MiniMax dosyalari
needed=[
 COMFY+"/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
 COMFY+"/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
 COMFY+"/models/vae/minimax_h3_video_vae_int8_convrot.safetensors",
 COMFY+"/models/vae/minimax_h3_audio_vae_fp32.safetensors",
]
missing=[p for p in needed if not os.path.exists(p)]
if missing:
    print("UYARI - eksik model dosyalari:")
    print("\n".join(missing))

# Ayni porttaki eski ComfyUI'yi kullan; yoksa baslat.
def alive():
    try:
        return urllib.request.urlopen("http://127.0.0.1:8188/system_stats",timeout=2).status == 200
    except:
        return False

if not alive():
    log=open("/content/comfy_minimax.log","w")
    subprocess.Popen(
        [sys.executable,"-u",COMFY+"/main.py","--listen","127.0.0.1","--port","8188"],
        cwd=COMFY, stdout=log, stderr=subprocess.STDOUT
    )
    for _ in range(120):
        if alive(): break
        time.sleep(2)
    else:
        log.flush()
        print(open("/content/comfy_minimax.log",errors="ignore").read()[-8000:])
        raise RuntimeError("ComfyUI baslamadi")

print("MINIMAX-H3 / COMFYUI HAZIR")
print("Drive:", BASE)
print("ComfyUI: http://127.0.0.1:8188")

# Tunelsiz: Colab oturumu icinde ComfyUI.
output.serve_kernel_port_as_iframe(8188, height=1000)
