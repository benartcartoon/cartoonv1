#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DRIVE_ROOT="${CARTOON_DRIVE:-/content/drive/MyDrive/CartoonV1}"
WAN_CODE="/content/Wan2.1"
WAN_MODEL="$DRIVE_ROOT/models/wan2"
FP8_T5="$WAN_MODEL/umt5-xxl-enc-fp8_e4m3fn.safetensors"
TOKENIZER_DIR="$WAN_MODEL/google/umt5-xxl"

[[ -d /content/drive/MyDrive ]] || { echo "HATA: Google Drive bagli degil."; exit 1; }
command -v nvidia-smi >/dev/null 2>&1 || { echo "HATA: GPU acik degil. Colab'da T4 sec."; exit 2; }

mkdir -p "$DRIVE_ROOT"/{models,characters,cache,scenes,audio,output,temp,env_cache}

for f in config.json diffusion_pytorch_model.safetensors Wan2.1_VAE.pth; do
  [[ -s "$WAN_MODEL/$f" ]] || { echo "HATA: Wan model dosyasi eksik: $WAN_MODEL/$f"; exit 3; }
done

echo "=============================================="
echo "CartoonV1 LOW-RAM - Wan2.1 T2V 1.3B"
echo "Drive modeli: $WAN_MODEL"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo "RAM: $(free -h | awk '/Mem:/ {print $2}')"
echo "=============================================="

apt-get update -qq
apt-get install -y -qq ffmpeg git >/dev/null
python3 -m pip install -q huggingface_hub

if [[ ! -s "$FP8_T5" ]]; then
  echo "FP8 T5 ilk kez Drive'a indiriliyor..."
  hf download Kijai/WanVideo_comfy umt5-xxl-enc-fp8_e4m3fn.safetensors --local-dir "$WAN_MODEL"
fi

# The FP8 Wan fork resolves t5_tokenizer relative to ckpt_dir. Keep the small
# Google UMT5 tokenizer files at exactly ckpt_dir/google/umt5-xxl.
if [[ ! -s "$TOKENIZER_DIR/tokenizer_config.json" ]]; then
  echo "UMT5 tokenizer dosyalari Drive'a hazirlaniyor..."
  mkdir -p "$TOKENIZER_DIR"
  python3 - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="google/umt5-xxl",
    local_dir="/content/drive/MyDrive/CartoonV1/models/wan2/google/umt5-xxl",
    allow_patterns=["tokenizer*", "spiece.model", "special_tokens_map.json", "config.json"],
)
PY
fi

rm -rf "$WAN_CODE"
git clone -q https://github.com/YexiongLin/Wan2.1.git "$WAN_CODE"
cd "$WAN_CODE"
git checkout -q 36d6d91

python3 - <<'PY'
from pathlib import Path
p=Path('/content/Wan2.1/wan/configs/wan_t2v_1_3B.py')
s=p.read_text()
s=s.replace("models_t5_umt5-xxl-enc-bf16.pth", "umt5-xxl-enc-fp8_e4m3fn.safetensors")
p.write_text(s)
PY

export PIP_CACHE_DIR="$DRIVE_ROOT/cache/pip"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TOKENIZERS_PARALLELISM=false
export MALLOC_ARENA_MAX=2
mkdir -p "$PIP_CACHE_DIR"

grep -viE '^flash[_-]attn([<=> ].*)?$' "$WAN_CODE/requirements.txt" > /tmp/wan_requirements_t4.txt
python3 -m pip install -q -r /tmp/wan_requirements_t4.txt
python3 -m pip install -q accelerate safetensors
python3 -m pip install -q -r "$ROOT/requirements.txt"

python3 "$ROOT/scripts/pipeline.py" \
  --config "$ROOT/config/project.yaml" \
  --story "$ROOT/story/story.yaml" \
  --characters "$ROOT/characters/characters.yaml"
