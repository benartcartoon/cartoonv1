#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/workflows/official"

curl -L --fail --retry 3 \
  -o "$ROOT/workflows/official/image_to_video_wan22_5B.json" \
  "https://raw.githubusercontent.com/comfyanonymous/ComfyUI_examples/master/wan22/image_to_video_wan22_5B.json"

curl -L --fail --retry 3 \
  -o "$ROOT/workflows/official/text_to_video_wan22_5B.json" \
  "https://raw.githubusercontent.com/comfyanonymous/ComfyUI_examples/master/wan22/text_to_video_wan22_5B.json"

echo "Official Wan 2.2 5B workflows downloaded."
