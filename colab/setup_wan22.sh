#!/usr/bin/env bash
set -e
ROOT="/content/drive/MyDrive/Wan2.2-Cartoon"
APP="/content/Wan2.2"
mkdir -p "$ROOT"/{models,input,output,characters}
if [ ! -d "$APP/.git" ]; then
  git clone -q https://github.com/Wan-Video/Wan2.2.git "$APP"
fi
cd "$APP"
pip -q install -r requirements.txt
pip -q install "huggingface_hub[cli]" gradio
echo "WAN2.2 hazir. Modeller: $ROOT/models"
echo "Input: $ROOT/input | Output: $ROOT/output | Characters: $ROOT/characters"
