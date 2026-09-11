#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cartoonv1"
COMFY="$HOME/ComfyUI"

source "$COMFY/.venv/bin/activate"
cd "$COMFY"
python main.py --listen 127.0.0.1 --port 8188 > "$HOME/comfyui.log" 2>&1 &
COMFY_PID=$!

echo "ComfyUI başlatıldı (PID $COMFY_PID)."
cd "$ROOT"
python scripts/run.py
