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

if [[ ! -s "$TOKENIZER_DIR/tokenizer_config.json" ]]; then
  echo "UMT5 tokenizer dosyalari Drive'a hazirlaniyor..."
  mkdir -p "$TOKENIZER_DIR"
  hf download google/umt5-xxl --include 'config.json' 'tokenizer.json' 'tokenizer_config.json' 'special_tokens_map.json' 'spiece.model' --local-dir "$TOKENIZER_DIR"
fi

rm -rf "$WAN_CODE"
git clone -q https://github.com/YexiongLin/Wan2.1.git "$WAN_CODE"
cd "$WAN_CODE"
git checkout -q 36d6d91

# Point Wan 1.3B at the FP8 text encoder kept on Drive.
python3 - <<'PY'
from pathlib import Path
p=Path('/content/Wan2.1/wan/configs/wan_t2v_1_3B.py')
s=p.read_text()
s=s.replace("models_t5_umt5-xxl-enc-bf16.pth", "umt5-xxl-enc-fp8_e4m3fn.safetensors")
p.write_text(s)

# This FP8 fork calls flash_attention() directly in model.py. Tesla T4 cannot
# use FlashAttention-2, so route those calls through Wan's built-in SDPA
# fallback function instead.
p=Path('/content/Wan2.1/wan/modules/model.py')
s=p.read_text()
s=s.replace('from .attention import flash_attention', 'from .attention import attention')
s=s.replace('flash_attention(', 'attention(')
p.write_text(s)
PY

export PIP_CACHE_DIR="$DRIVE_ROOT/cache/pip"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TOKENIZERS_PARALLELISM=false
export MALLOC_ARENA_MAX=2
mkdir -p "$PIP_CACHE_DIR"

# Do not install FlashAttention on Tesla T4. Wan's attention() falls back to
# torch.nn.functional.scaled_dot_product_attention when FA2/FA3 is absent.
grep -viE '^flash[_-]attn([<=> ].*)?$' "$WAN_CODE/requirements.txt" > /tmp/wan_requirements_t4.txt
python3 -m pip install -q -r /tmp/wan_requirements_t4.txt
python3 -m pip install -q accelerate safetensors
python3 -m pip install -q -r "$ROOT/requirements.txt"

python3 "$ROOT/scripts/pipeline.py" \
  --config "$ROOT/config/project.yaml" \
  --story "$ROOT/story/story.yaml" \
  --characters "$ROOT/characters/characters.yaml"
