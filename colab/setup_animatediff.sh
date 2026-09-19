#!/usr/bin/env bash
set -e

ROOT="/content/drive/MyDrive/AnimateDiff-Colab"
WEBUI="/content/stable-diffusion-webui"

mkdir -p "$ROOT"/{models,characters,input,output,config}

if [ ! -d "$WEBUI/.git" ]; then
  git clone --branch v1.10.1 https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "$WEBUI"
fi

if [ ! -d "$WEBUI/extensions/sd-webui-animatediff/.git" ]; then
  git clone https://github.com/continue-revolution/sd-webui-animatediff.git "$WEBUI/extensions/sd-webui-animatediff"
fi

mkdir -p "$WEBUI/models/Stable-diffusion" "$WEBUI/extensions/sd-webui-animatediff/model"

# Drive'daki checkpointleri A1111'e bagla; motion modeli checkpoint olarak eklenmez.
find "$ROOT/models" -maxdepth 1 -type f \( -name "*.safetensors" -o -name "*.ckpt" \) ! -name "mm_sd15_v2.safetensors" -exec ln -sf {} "$WEBUI/models/Stable-diffusion/" \;

# AnimateDiff motion module
if [ -f "$ROOT/models/mm_sd15_v2.safetensors" ]; then
  ln -sf "$ROOT/models/mm_sd15_v2.safetensors" "$WEBUI/extensions/sd-webui-animatediff/model/mm_sd15_v2.safetensors"
else
  wget -q --show-progress -O "$ROOT/models/mm_sd15_v2.safetensors" "https://huggingface.co/conrevo/AnimateDiff-A1111/resolve/main/motion_module/mm_sd15_v2.safetensors?download=true"
  ln -sf "$ROOT/models/mm_sd15_v2.safetensors" "$WEBUI/extensions/sd-webui-animatediff/model/mm_sd15_v2.safetensors"
fi

# Ciktilari kalici olarak Drive'a yaz.
rm -rf "$WEBUI/outputs"
ln -s "$ROOT/output" "$WEBUI/outputs"

cd "$WEBUI"

# A1111 v1.10.1'in kaldirilmis eski SD deposuna gitmesini engelle.
export STABLE_DIFFUSION_REPO="https://github.com/w-e-w/stablediffusion.git"

# Colab Python 3.13'te eski xformers 0.0.23.post1 derlenemiyor.
# xformers'i zorlamadan Colab'in CUDA/PyTorch attention altyapisini kullan.
export COMMANDLINE_ARGS="--listen --share --api --opt-sdp-attention --skip-python-version-check --enable-insecure-extension-access"

python launch.py
