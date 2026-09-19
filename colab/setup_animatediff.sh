#!/usr/bin/env bash
set -e

ROOT="/content/drive/MyDrive/AnimateDiff-Colab"
WEBUI="/content/stable-diffusion-webui"
PYENV="/content/a1111-py310"
MAMBA_ROOT_PREFIX="/content/micromamba"

mkdir -p "$ROOT"/{models,characters,input,output,config}

if [ ! -x "$PYENV/bin/python" ]; then
  echo "Python 3.10 ortami hazirlaniyor..."
  if [ ! -x /content/bin/micromamba ]; then
    cd /content
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
  fi
  MAMBA_ROOT_PREFIX="$MAMBA_ROOT_PREFIX" /content/bin/micromamba create -y -p "$PYENV" -c conda-forge python=3.10 pip
fi

PYTHON="$PYENV/bin/python"
"$PYTHON" -m pip install -q --force-reinstall "pip==24.0" "setuptools==69.5.1" "wheel==0.43.0" "packaging<25"

if [ ! -d "$WEBUI/.git" ]; then
  git clone --branch v1.10.1 https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "$WEBUI"
fi

if [ ! -d "$WEBUI/extensions/sd-webui-animatediff/.git" ]; then
  git clone https://github.com/continue-revolution/sd-webui-animatediff.git "$WEBUI/extensions/sd-webui-animatediff"
fi

# Character consistency: install ControlNet so AnimateDiff can use a reference image
# (reference_adain+attn requires no separate ControlNet model download).
if [ ! -d "$WEBUI/extensions/sd-webui-controlnet/.git" ]; then
  git clone https://github.com/Mikubill/sd-webui-controlnet.git "$WEBUI/extensions/sd-webui-controlnet"
fi

mkdir -p "$WEBUI/models/Stable-diffusion" "$WEBUI/extensions/sd-webui-animatediff/model"

# Always expose the Disney checkpoint from Drive and fail early if it is missing.
DISNEY="$ROOT/models/disneyPixarCartoon_v10.safetensors"
if [ ! -s "$DISNEY" ]; then
  echo "HATA: Disney checkpoint Drive'da bulunamadi: $DISNEY"
  exit 1
fi
ln -sf "$DISNEY" "$WEBUI/models/Stable-diffusion/disneyPixarCartoon_v10.safetensors"

# Also expose any other user checkpoints stored in Drive.
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

# A1111 v1.10.1 / torch 2.1.x and scikit-image wheels require NumPy 1.x ABI.
# ControlNet may otherwise pull NumPy 2.x and break startup.
"$PYTHON" -m pip install -q --force-reinstall "numpy==1.26.4" "opencv-python==4.10.0.84" "opencv-python-headless==4.10.0.84" "opencv-contrib-python==4.10.0.84" "mediapipe==0.10.14"

# AnimateDiff recommends padding positive/negative conditioning to the same length.
# This reduces unrelated temporal branches between prompt conditions.
"$PYTHON" - <<'PY'
import json, os
p="/content/stable-diffusion-webui/config.json"
try:
    d=json.load(open(p)) if os.path.exists(p) else {}
except Exception:
    d={}
d["pad_cond_uncond"]=True
d["sd_model_checkpoint"]="disneyPixarCartoon_v10.safetensors"
d["samples_format"]="png"
d["grid_format"]="png"
d["samples_save"]=True
d["grid_save"]=False
with open(p,"w") as f:
    json.dump(d,f,indent=2)
print("Character consistency settings enabled.")
PY

export STABLE_DIFFUSION_REPO="https://github.com/w-e-w/stablediffusion.git"
export python_cmd="$PYTHON"

# Colab notebook MPLBACKEND degeri izole env'deki matplotlib tarafindan taninmiyor.
# WebUI GUI'siz calistigi icin guvenli non-interactive backend kullan.
export MPLBACKEND="Agg"

export COMMANDLINE_ARGS="--listen --share --api --opt-sdp-attention --enable-insecure-extension-access --ckpt \"$DISNEY\""
"$PYTHON" launch.py
