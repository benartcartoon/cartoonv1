#!/usr/bin/env bash
set -euo pipefail
SA3="/content/drive/MyDrive/Çizgi Film YouTube 1/models/stable-audio-3"
echo "=== Stable Audio 3 MEDIUM 1.4B geçişi ==="
test -x "$SA3/.venv/bin/python" || { echo "HATA: Python 3.10 venv bulunamadı"; exit 2; }
cd "$SA3"
PY="$SA3/.venv/bin/python"
"$PY" -V

# uv is global in Colab; explicitly target the existing Python 3.10 venv.
UV_BIN="$(command -v uv || true)"
if [ -z "$UV_BIN" ]; then
  python -m pip install -q uv
  UV_BIN="$(command -v uv)"
fi
echo "uv: $UV_BIN"

"$UV_BIN" pip install --python "$PY" --no-deps   "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.6.3+cu126torch2.7-cp310-cp310-linux_x86_64.whl"

"$PY" -c "import flash_attn; from flash_attn import flash_attn_func; print('Flash Attention OK:', flash_attn.__version__)"
echo
echo "MEDIUM altyapısı hazır."
echo "Model ID: medium (1.4B)"
echo "Not: gated model indirmesi için Colab oturumunda HF_TOKEN/login gerekir."
echo "tamamlandı"
