#!/usr/bin/env bash
set -euo pipefail

ROOT="/content/drive/MyDrive/Çizgi Film YouTube 1"
APP="$ROOT/models/HunyuanVideo-Foley"
WEIGHTS="$ROOT/models/HunyuanVideo-Foley-weights"

echo "=== HunyuanVideo-Foley XXL / Drive kurulumu ==="

# Drive must already be mounted by the Colab kernel.
test -d /content/drive/MyDrive || { echo "HATA: Önce Google Drive'ı Colab'a bağla."; exit 2; }

mkdir -p "$ROOT/models" "$ROOT/audio/foley" "$ROOT/cache/huggingface"

if [ ! -d "$APP/.git" ]; then
  git clone https://github.com/Tencent-Hunyuan/HunyuanVideo-Foley.git "$APP"
else
  git -C "$APP" pull --ff-only
fi

# Separate environment so Stable Audio dependencies are not mixed with Foley.
python3 -m venv "$APP/.venv"
"$APP/.venv/bin/python" -m pip install -U pip setuptools wheel
"$APP/.venv/bin/pip" install -r "$APP/requirements.txt"
"$APP/.venv/bin/pip" install -U "huggingface_hub[cli]"

# Keep HF cache and the final model on Drive.
export HF_HOME="$ROOT/cache/huggingface"
export HUGGINGFACE_HUB_CACHE="$ROOT/cache/huggingface/hub"
mkdir -p "$WEIGHTS"

echo
echo "Kod hazır: $APP"
echo "XXL ağırlık hedefi: $WEIGHTS"
echo "Sonraki adım: resmi Tencent ağırlıklarını Hugging Face'den doğrudan bu Drive klasörüne indirmek."
echo "T4 için çalıştırma modu: XXL + --enable_offload (resmi tabloda ~12 GB VRAM)."
echo "tamamlandı"
