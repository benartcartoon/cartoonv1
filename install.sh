#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cartoonv1"
COMFY="$HOME/ComfyUI"

echo "[1/4] Sistem paketleri"
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip ffmpeg

if [ ! -d "$COMFY/.git" ]; then
  echo "[2/4] ComfyUI indiriliyor"
  git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFY"
else
  echo "[2/4] ComfyUI zaten mevcut"
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

echo "[3/4] Klasörler hazırlanıyor"
mkdir -p "$ROOT/outputs" "$ROOT/characters/images"

echo "[4/4] Tamam"
echo "Sonraki adım: model ve workflow dosyalarını bağlamak."
