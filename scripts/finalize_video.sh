#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-outputs/combined_raw.mp4}"
OUTPUT="${2:-outputs/cartoonv1_final_1080p60.mp4}"

if [ ! -f "$INPUT" ]; then
  echo "Input video not found: $INPUT"
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

ffmpeg -y -i "$INPUT" \
  -vf "scale=1920:1080:flags=lanczos,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  "$OUTPUT"

echo "Final video ready: $OUTPUT"
