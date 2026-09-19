#!/usr/bin/env bash
set -euo pipefail
ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
APP="/content/Wan2.2"
MARKER="/content/.wan22_deps_v2_ready"

mkdir -p "$ROOT"/{models,input,output,characters}

echo "[1/5] WAN2.2 kodu kontrol ediliyor..."
if [ ! -d "$APP/.git" ]; then
  git clone -q --depth 1 https://github.com/Wan-Video/Wan2.2.git "$APP"
fi

echo "[2/5] Model kontrol ediliyor..."
test -f "$ROOT/models/Wan2.2-TI2V-5B/config.json" || { echo "HATA: TI2V-5B Drive'da bulunamadi."; exit 1; }

echo "[3/5] Colab paket cakismalari temizleniyor..."
python -m pip uninstall -y -q jax jaxlib flax optax orbax-checkpoint chex || true

echo "[4/5] WAN2.2 uyumlu surumler kuruluyor..."\necho "    -> numpy / transformers / diffusers / gradio kuruluyor; bu kisim birkaç dakika surebilir..."
# Resmi WAN2.2: numpy<2 ve transformers<=4.51.3.
python -m pip install --progress-bar on --disable-pip-version-check --upgrade --force-reinstall   "numpy==1.26.4"   "transformers==4.51.3"   "diffusers==0.35.2"   "huggingface-hub==0.36.0"   "gradio==5.49.1"
cd "$APP"
grep -viE '^[[:space:]]*(flash[-_]attn|numpy|transformers|diffusers)' requirements.txt > /tmp/wan22_requirements.txt
echo "    -> WAN2.2 ana gereksinimleri kuruluyor (pip ayrintilari asagida)..."\npython -m pip install --progress-bar on --disable-pip-version-check -r /tmp/wan22_requirements.txt
touch "$MARKER"

echo "[4.5/5] Eksik WAN modulleri kontrol ediliyor..."
echo "    -> decord kuruluyor..."\npython -m pip install --progress-bar on --disable-pip-version-check decord
echo "FlashAttention 2 hazir wheel kuruluyor..."
python -m pip install --progress-bar on --disable-pip-version-check "https://github.com/lesj0610/flash-attention/releases/download/v2.8.3-cu12-torch2.11/flash_attn-2.8.3%2Bcu12torch2.11cxx11abiTRUE-cp313-cp313-linux_x86_64.whl"
python - <<'PY'
import flash_attn, torch
print("flash-attn:", flash_attn.__version__)
print("torch:", torch.__version__, "cuda:", torch.version.cuda)
PY

echo "[4.7/5] Senkron video-to-audio sistemi kuruluyor..."\necho "    -> MMAudio kodu ve bagimliliklari hazirlaniyor..."
if [ ! -d /content/MMAudio/.git ]; then
  git clone -q --depth 1 https://github.com/hkchengrex/MMAudio.git /content/MMAudio
fi
# Keep the already-working Colab torch/CUDA stack; install MMAudio without replacing torch.
echo "    -> MMAudio Python paketleri kuruluyor..."\npython -m pip install --progress-bar on --disable-pip-version-check -e /content/MMAudio

echo "[5/5] Surum kontrolu ve web arayuzu..."
python - <<'PY'
import numpy, transformers, diffusers
print("numpy:", numpy.__version__)
print("transformers:", transformers.__version__)
print("diffusers:", diffusers.__version__)
PY
cd "$APP"
exec python /content/cartoonv1/colab/wan22_webui.py
