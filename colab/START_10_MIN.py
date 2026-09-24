from google.colab import drive
import os, subprocess, shutil
if not os.path.ismount("/content/drive"):
    drive.mount("/content/drive")
subprocess.run(["bash","-lc","rm -rf /content/cartoonv1 && git clone -q --depth 1 https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1"],check=True)

episode="/content/drive/MyDrive/MiniMax-H3/episodes/episode_001"
os.makedirs(episode,exist_ok=True)
plan=os.path.join(episode,"plan.json")
if not os.path.exists(plan):
    shutil.copy2("/content/cartoonv1/episodes/episode_001.plan.json",plan)

model="/content/drive/MyDrive/Wan2.2-Cartoon/models/Wan2.2-TI2V-5B/config.json"
if not os.path.exists(model):
    raise RuntimeError("WAN2.2 modeli Drive'da bulunamadi: "+model)

if not os.path.exists("/content/Wan2.2/generate.py"):
    subprocess.run(["git","clone","--depth","1","https://github.com/Wan-Video/Wan2.2.git","/content/Wan2.2"],check=True)
    subprocess.run(["bash","-lc","grep -viE '^[[:space:]]*(flash[-_]attn)' /content/Wan2.2/requirements.txt > /tmp/wan_req.txt && pip -q install -r /tmp/wan_req.txt"],check=True)

print("10 DAKIKALIK BOLUM BASLIYOR - tamamlanan sahneler Drive'da korunur.")
subprocess.run(["python","/content/cartoonv1/scripts/render_episode.py"],check=True)
