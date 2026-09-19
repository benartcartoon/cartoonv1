#!/usr/bin/env bash
set -euo pipefail

ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
APP="/content/Wan2.2"

stage(){ echo; echo "============================================================"; echo "$1"; echo "============================================================"; }

stage "[0/7] GPU / CUDA kontrol ediliyor..."
python - <<'PY'
import sys, torch
print("Python:", sys.version.split()[0])
print("Torch:", torch.__version__)
print("CUDA build:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
if not torch.cuda.is_available() or torch.version.cuda is None:
    raise SystemExit("HATA: GPU/CUDA aktif degil. Colab Runtime type -> A100 GPU secip yeniden calistirin.")
print("GPU:", torch.cuda.get_device_name(0))
PY

mkdir -p "$ROOT"/{models,input,output,characters}

stage "[1/7] WAN2.2 kodu kontrol ediliyor..."
if [ ! -d "$APP/.git" ]; then
  git clone --depth 1 https://github.com/Wan-Video/Wan2.2.git "$APP"
else
  echo "OK: WAN2.2 kodu zaten mevcut."
fi

stage "[2/7] Drive modeli kontrol ediliyor..."
test -f "$ROOT/models/Wan2.2-TI2V-5B/config.json" || { echo "HATA: Drive'daki TI2V-5B modeli bulunamadi."; exit 1; }
echo "OK: Drive modeli bulundu; tekrar indirilmeyecek."

stage "[3/7] Temel Python paketleri kuruluyor..."
python -m pip uninstall -y -q jax jaxlib flax optax orbax-checkpoint chex || true
python -m pip install --progress-bar on --disable-pip-version-check --upgrade \
  "numpy>=2.1,<2.3" \
  "transformers==4.51.3" \
  "diffusers==0.35.2" \
  "huggingface-hub==0.36.0" \
  "gradio==5.49.1"

stage "[4/7] WAN2.2 gereksinimleri kuruluyor..."
cd "$APP"
grep -viE '^[[:space:]]*(flash[-_]attn|numpy|transformers|diffusers)' requirements.txt > /tmp/wan22_requirements.txt
python -m pip install --progress-bar on --disable-pip-version-check -r /tmp/wan22_requirements.txt
python -m pip install --progress-bar on --disable-pip-version-check decord

stage "[5/7] FlashAttention kuruluyor ve test ediliyor..."
python -m pip install --progress-bar on --disable-pip-version-check \
  "https://github.com/lesj0610/flash-attention/releases/download/v2.8.3-cu12-torch2.11/flash_attn-2.8.3%2Bcu12torch2.11cxx11abiTRUE-cp313-cp313-linux_x86_64.whl"
python - <<'PY'
import torch, flash_attn
print("Torch:", torch.__version__, "CUDA:", torch.version.cuda)
print("GPU:", torch.cuda.get_device_name(0))
print("FlashAttention:", flash_attn.__version__)
PY

stage "[6/7] MMAudio senkron ses sistemi kuruluyor..."
if [ ! -d /content/MMAudio/.git ]; then
  git clone --depth 1 https://github.com/hkchengrex/MMAudio.git /content/MMAudio
else
  echo "OK: MMAudio kodu zaten mevcut."
fi
# MMAudio metadata pins numpy<2.1; on Python 3.13 that selects a source tarball.
# We already have a working cp313 NumPy wheel, so keep it and install MMAudio deps without dependency re-resolution.
python -m pip install --progress-bar on --disable-pip-version-check \
  "av>=14.0.1" colorlog "gitpython>=3.1" hydra-colorlog "hydra-core>=1.3.2" nitrous-ema
python -m pip install --progress-bar on --disable-pip-version-check --no-deps -e /content/MMAudio
echo "OK: MMAudio kuruldu; Python 3.13 NumPy wheel korunuyor."

stage "[7/7] Son kontrol ve CartoonV1 arayuzu..."
python - <<'PY'
import torch, numpy, transformers, diffusers
assert torch.cuda.is_available(), "CUDA kayboldu"
print("GPU:", torch.cuda.get_device_name(0))
print("Torch:", torch.__version__, "CUDA:", torch.version.cuda)
print("NumPy:", numpy.__version__)
print("Transformers:", transformers.__version__)
print("Diffusers:", diffusers.__version__)
print("OK: Kurulum kontrolleri basarili.")
PY

cd "$APP"
exec python /content/cartoonv1/colab/wan22_webui.py
