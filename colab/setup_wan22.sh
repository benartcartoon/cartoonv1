#!/usr/bin/env bash
set -euo pipefail
ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
APP="/content/Wan2.2"
MARKER="$ROOT/.wan22_deps_ready"

mkdir -p "$ROOT"/{models,input,output,characters}

echo "[1/4] WAN2.2 kodu kontrol ediliyor..."
if [ ! -d "$APP/.git" ]; then
  git clone -q --depth 1 https://github.com/Wan-Video/Wan2.2.git "$APP"
else
  git -C "$APP" pull -q --ff-only || true
fi

echo "[2/4] Model kontrol ediliyor..."
test -f "$ROOT/models/Wan2.2-TI2V-5B/config.json" || { echo "HATA: TI2V-5B Drive'da bulunamadi."; exit 1; }

echo "[3/4] Python paketleri kontrol ediliyor..."
if [ ! -f "$MARKER" ]; then
  cd "$APP"
  # flash-attn ilk acilista uzun derlenebiliyor; A100 testinde zorunlu degil.
  grep -viE '^[[:space:]]*flash[-_]attn' requirements.txt > /tmp/wan22_requirements.txt
  python -m pip install -q --disable-pip-version-check -r /tmp/wan22_requirements.txt
  python -m pip install -q --disable-pip-version-check "gradio>=4.44,<6" pillow
  touch "$MARKER"
else
  echo "Paket kurulumu daha once tamamlanmis; tekrar atlandi."
fi

echo "[4/4] Web arayuzu baslatiliyor..."
cd "$APP"
exec python /content/cartoonv1/colab/wan22_webui.py
