#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DRIVE_ROOT="${CARTOON_DRIVE:-/content/drive/MyDrive/CartoonV1}"

[[ -d /content/drive/MyDrive ]] || { echo "HATA: Google Drive bagli degil."; exit 1; }
command -v nvidia-smi >/dev/null 2>&1 || { echo "HATA: GPU acik degil. Colab'da T4 sec."; exit 2; }

mkdir -p "$DRIVE_ROOT"/{models,characters,cache,scenes,output}

echo "=============================================="
echo "CartoonV1 ONE CLICK"
echo "Drive: $DRIVE_ROOT"
echo "=============================================="

python3 -m pip install -q -r "$ROOT/requirements.txt"
python3 "$ROOT/scripts/pipeline.py" --config "$ROOT/config/project.yaml" --story "$ROOT/story/story.yaml" --characters "$ROOT/characters/characters.yaml"
