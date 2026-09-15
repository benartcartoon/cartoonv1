#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DRIVE_ROOT="${CARTOON_DRIVE:-/content/drive/MyDrive/CartoonV1}"
WAN_CODE="/content/Wan2.1"
WAN_MODEL="$DRIVE_ROOT/models/wan2"

[[ -d /content/drive/MyDrive ]] || { echo "HATA: Google Drive bagli degil."; exit 1; }
command -v nvidia-smi >/dev/null 2>&1 || { echo "HATA: GPU acik degil. Colab'da T4 sec."; exit 2; }

mkdir -p "$DRIVE_ROOT"/{models,characters,cache,scenes,audio,output,temp,env_cache}

for f in config.json diffusion_pytorch_model.safetensors models_t5_umt5-xxl-enc-bf16.pth Wan2.1_VAE.pth; do
  [[ -s "$WAN_MODEL/$f" ]] || { echo "HATA: Wan model dosyasi eksik: $WAN_MODEL/$f"; exit 3; }
done

echo "=============================================="
echo "CartoonV1 ONE CLICK - Wan2.1 T2V 1.3B"
echo "Drive modeli: $WAN_MODEL"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo "=============================================="

apt-get update -qq
apt-get install -y -qq ffmpeg git >/dev/null
rm -rf "$WAN_CODE"
git clone -q --depth 1 https://github.com/Wan-Video/Wan2.1.git "$WAN_CODE"

export PIP_CACHE_DIR="$DRIVE_ROOT/cache/pip"
mkdir -p "$PIP_CACHE_DIR"

# Colab T4 is Turing; current FlashAttention-2 does not support T4.
# Install Wan dependencies except flash_attn. Wan falls back to PyTorch SDPA.
grep -viE '^flash[_-]attn([<=> ].*)?$' "$WAN_CODE/requirements.txt" > /tmp/wan_requirements_t4.txt
python3 -m pip install -q -r /tmp/wan_requirements_t4.txt
python3 -m pip install -q -r "$ROOT/requirements.txt"

python3 "$ROOT/scripts/pipeline.py" \
  --config "$ROOT/config/project.yaml" \
  --story "$ROOT/story/story.yaml" \
  --characters "$ROOT/characters/characters.yaml"
