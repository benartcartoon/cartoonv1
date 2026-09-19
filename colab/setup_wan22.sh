#!/usr/bin/env bash
set -e
ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
APP="/content/Wan2.2"
mkdir -p "$ROOT"/{models,input,output,characters}
if [ ! -d "$APP/.git" ]; then git clone -q https://github.com/Wan-Video/Wan2.2.git "$APP"; fi
cd "$APP"
pip -q install -r requirements.txt
pip -q install "huggingface_hub[cli]" "gradio>=4.36"
test -d "$ROOT/models/Wan2.2-TI2V-5B" || echo "UYARI: TI2V-5B modeli Drive'da henüz yok."
python /content/cartoonv1/colab/wan22_webui.py
