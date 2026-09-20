#!/usr/bin/env bash
set -e

DRIVE_ROOT="/content/drive/MyDrive/Çizgi Film YouTube 1"
REPO_DIR="/content/cartoonv1"
SA3_DIR="$DRIVE_ROOT/models/stable-audio-3"

echo "=== Stable Audio 3 Small-SFX kurulumu ==="

# Drive mounting MUST happen in the Colab notebook kernel, not in a shell subprocess.
if [ ! -d "/content/drive/MyDrive" ]; then
  echo "HATA: Google Drive bağlı değil."
  echo "Önce Colab hücresinde: from google.colab import drive; drive.mount('/content/drive')"
  exit 2
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/benartcartoon/cartoonv1.git "$REPO_DIR"
else
  git -C "$REPO_DIR" pull
fi

python -m pip install -q uv

if [ ! -d "$SA3_DIR/.git" ]; then
  mkdir -p "$(dirname "$SA3_DIR")"
  git clone https://github.com/Stability-AI/stable-audio-3.git "$SA3_DIR"
else
  git -C "$SA3_DIR" pull
fi

cd "$SA3_DIR"
uv sync
mkdir -p "$DRIVE_ROOT/audio/test"

echo
echo "Kurulum tamamlandı."
echo "tamamlandı"
