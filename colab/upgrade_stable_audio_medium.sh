#!/usr/bin/env bash
set -euo pipefail

SA3="/content/drive/MyDrive/Çizgi Film YouTube 1/models/stable-audio-3"

echo "=== Stable Audio 3 MEDIUM 1.4B geçişi ==="
test -d "$SA3/.venv" || { echo "HATA: Stable Audio 3 kurulumu bulunamadı"; exit 2; }
cd "$SA3"

# IMPORTANT: Colab system Python is currently 3.13, but this project's venv is Python 3.10.
# Never use bare 'uv pip' here because it can target /usr (cp313).
PY="$SA3/.venv/bin/python"
UV="$SA3/.venv/bin/uv"

"$PY" -V

# Medium requires Flash Attention 2. Install the cp310 / CUDA 12.6 / torch 2.7 wheel
# directly into the existing Python 3.10 virtualenv.
"$UV" pip install --python "$PY" --no-deps   "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.6.3+cu126torch2.7-cp310-cp310-linux_x86_64.whl"

"$PY" -c "import flash_attn; from flash_attn import flash_attn_func; print('Flash Attention OK:', flash_attn.__version__)"

echo
echo "MEDIUM altyapısı hazır."
echo "Model ID: medium (1.4B)"
echo "Not: gated model indirmesi için Colab oturumunda HF_TOKEN/login gerekir."
echo "tamamlandı"
