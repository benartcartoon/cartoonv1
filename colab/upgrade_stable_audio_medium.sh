#!/usr/bin/env bash
set -e

SA3="/content/drive/MyDrive/Çizgi Film YouTube 1/models/stable-audio-3"

echo "=== Stable Audio 3 MEDIUM 1.4B geçişi ==="
test -d "$SA3/.venv" || { echo "HATA: Stable Audio 3 kurulumu bulunamadı"; exit 2; }
cd "$SA3"

# Official SA3 README: Medium requires Flash Attention 2.
uv pip install "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.6.3+cu126torch2.7-cp310-cp310-linux_x86_64.whl"

uv run python -c "import flash_attn; from flash_attn import flash_attn_func; print('Flash Attention OK:', flash_attn.__version__)"

echo
echo "MEDIUM altyapısı hazır."
echo "Model ID: medium (1.4B)"
echo "Not: Hugging Face gated model erişimi için Colab oturumunda HF_TOKEN/login gerekir."
echo "tamamlandı"
