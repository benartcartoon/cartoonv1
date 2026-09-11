#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cartoonv1"
COMFY="$HOME/ComfyUI"

echo "[1/5] Sistem paketleri"
sudo apt-get update
sudo apt-get install -y git curl python3 python3-venv python3-pip ffmpeg

if [ ! -d "$COMFY/.git" ]; then
  echo "[2/5] ComfyUI indiriliyor"
  git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFY"
else
  echo "[2/5] ComfyUI güncelleniyor"
  git -C "$COMFY" pull --ff-only || true
fi

if [ ! -d "$COMFY/.venv" ]; then
  python3 -m venv "$COMFY/.venv"
fi

source "$COMFY/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$COMFY/requirements.txt"

if [ -f "$ROOT/requirements.txt" ]; then
  pip install -r "$ROOT/requirements.txt"
fi

echo "[3/5] Klasörler hazırlanıyor"
mkdir -p "$ROOT/outputs/scenes" "$ROOT/characters/images"

echo "[4/5] Wan 2.2 5B model dosyaları kontrol ediliyor"
bash "$ROOT/models/install_wan22_5b.sh"

echo "[5/5] Kurulum tamam"
echo "Üretimi başlatmak için: cd ~/cartoonv1 && bash start.sh"
