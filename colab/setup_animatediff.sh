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
mkdir -p "$WEBUI/models/Stable-diffusion" "$WEBUI/extensions/sd-webui-animatediff/model" "$WEBUI/outputs"
find "$ROOT/models" -maxdepth 1 -type f \( -name "*.safetensors" -o -name "*.ckpt" \) -exec ln -sf {} "$WEBUI/models/Stable-diffusion/" \;
if [ -f "$ROOT/models/mm_sd15_v2.safetensors" ]; then
 ln -sf "$ROOT/models/mm_sd15_v2.safetensors" "$WEBUI/extensions/sd-webui-animatediff/model/mm_sd15_v2.safetensors"
else
 wget -q --show-progress -O "$ROOT/models/mm_sd15_v2.safetensors" "https://huggingface.co/conrevo/AnimateDiff-A1111/resolve/main/motion_module/mm_sd15_v2.safetensors?download=true"
 ln -sf "$ROOT/models/mm_sd15_v2.safetensors" "$WEBUI/extensions/sd-webui-animatediff/model/mm_sd15_v2.safetensors"
fi
rm -rf "$WEBUI/outputs"
ln -s "$ROOT/output" "$WEBUI/outputs"
cd "$WEBUI"
export COMMANDLINE_ARGS="--listen --share --api --xformers --enable-insecure-extension-access"
python launch.py
