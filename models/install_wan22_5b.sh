#!/usr/bin/env bash
set -euo pipefail

COMFY="${COMFY:-$HOME/ComfyUI}"
mkdir -p "$COMFY/models/diffusion_models" "$COMFY/models/vae" "$COMFY/models/text_encoders"

DL="curl -L --fail --retry 3 --continue-at -"

$DL -o "$COMFY/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors" \
  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors"

$DL -o "$COMFY/models/vae/wan2.2_vae.safetensors" \
  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors"

$DL -o "$COMFY/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"

echo "Wan2.2 5B model files installed."
