from google.colab import drive
import os, subprocess
if not os.path.ismount("/content/drive"):
    drive.mount("/content/drive")
subprocess.run(["bash","-lc","rm -rf /content/cartoonv1 && git clone -q --depth 1 https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1"],check=True)
print("1/2 WAN2.2 kurulumu/model kontrolu")
# setup_wan22.sh currently launches the manual UI, so automated production uses the existing WAN installation/model.
if not os.path.exists("/content/Wan2.2/generate.py"):
    subprocess.run(["git","clone","--depth","1","https://github.com/Wan-Video/Wan2.2.git","/content/Wan2.2"],check=True)
req="/content/Wan2.2/requirements.txt"
if os.path.exists(req):
    subprocess.run(["bash","-lc",f"grep -viE '^[[:space:]]*(flash[-_]attn)' {req} > /tmp/wan_req.txt && pip -q install -r /tmp/wan_req.txt"],check=True)
print("2/2 10 dakikalik bolum baslatiliyor")
subprocess.run(["python","/content/cartoonv1/scripts/render_episode.py"],check=True)
