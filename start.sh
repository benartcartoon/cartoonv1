#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cartoonv1"
COMFY="$HOME/ComfyUI"
TEST_SCENES="${TEST_SCENES:-0}"

source "$COMFY/.venv/bin/activate"

if ! curl -fsS http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
  cd "$COMFY"
  python main.py --listen 127.0.0.1 --port 8188 > "$HOME/comfyui.log" 2>&1 &
  echo "ComfyUI başlatıldı. Hazır olması bekleniyor..."
fi

cd "$ROOT"
python scripts/run.py
python scripts/build_scene_plan.py

if [ "$TEST_SCENES" -gt 0 ]; then
  echo "TEST MODU: İlk $TEST_SCENES sahne üretilecek."
  python scripts/comfy_generate.py --limit "$TEST_SCENES"
else
  python scripts/comfy_generate.py
fi

python scripts/assemble_video.py

echo ""
echo "TAMAMLANDI"
echo "Final video: $ROOT/outputs/cartoonv1_final_1080p60.mp4"
