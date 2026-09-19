#!/usr/bin/env bash
set -e

ROOT="/content/drive/MyDrive/AnimateDiff-Colab"
WEBUI="/content/stable-diffusion-webui"
PYENV="/content/a1111-py310"
MAMBA_ROOT_PREFIX="/content/micromamba"

mkdir -p "$ROOT"/{models,characters,input,output,config}

# Colab artik Python 3.13 kullaniyor. A1111 v1.10.1 icin izole Python 3.10 kur.
if [ ! -x "$PYENV/bin/python" ]; then
  echo "Python 3.10 ortami hazirlaniyor..."
  if [ ! -x /content/bin/micromamba ]; then
    cd /content
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
  fi
  MAMBA_ROOT_PREFIX="$MAMBA_ROOT_PREFIX" /content/bin/micromamba create -y -p "$PYENV" -c conda-forge python=3.10 pip
fi

PYTHON="$PYENV/bin/python"
"$PYTHON" -m pip install -q --upgrade "pip<25"

if [ ! -d "$WEBUI/.git" ]; then
  git clone --branch v1.10.1 https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "$WEBUI"
fi

if [ ! -d "$WEBUI/extensions/sd-webui-animatediff/.git" ]; then
  git clone https://github.com/continue-revolution/sd-webui-animatediff.git "$WEBUI/extensions/sd-webui-animatediff"
fi

mkdir -p "$WEBUI/models/Stable-diffusion" "$WEBUI/extensions/sd-webui-animatediff/model"

find "$ROOT/models" -maxdepth 1 -type f \( -name "*.safetensors" -o -name "*.ckpt" \) ! -name "mm_sd15_v2.safetensors" -exec ln -sf {} "$WEBUI/models/Stable-diffusion/" \;

if [ -f "$ROOT/models/mm_sd15_v2.safetensors" ]; then
  ln -sf "$ROOT/models/mm_sd15_v2.safetensors" "$WEBUI/extensions/sd-webui-animatediff/model/mm_sd15_v2.safetensors"
else
  wget -q --show-progress -O "$ROOT/models/mm_sd15_v2.safetensors" "https://huggingface.co/conrevo/AnimateDiff-A1111/resolve/main/motion_module/mm_sd15_v2.safetensors?download=true"
  ln -sf "$ROOT/models/mm_sd15_v2.safetensors" "$WEBUI/extensions/sd-webui-animatediff/model/mm_sd15_v2.safetensors"
fi

rm -rf "$WEBUI/outputs"
ln -s "$ROOT/output" "$WEBUI/outputs"

cd "$WEBUI"
export STABLE_DIFFUSION_REPO="https://github.com/w-e-w/stablediffusion.git"
export python_cmd="$PYTHON"
export COMMANDLINE_ARGS="--listen --share --api --opt-sdp-attention --enable-insecure-extension-access"

"$PYTHON" launch.py
