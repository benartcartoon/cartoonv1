#!/usr/bin/env bash
set -euo pipefail

ROOT="/content/drive/MyDrive/Çizgi Film YouTube 1"
APP="$ROOT/models/HunyuanVideo-Foley"
WEIGHTS="$ROOT/models/HunyuanVideo-Foley-weights"
ENV="/content/hunyuan-foley-env"

echo "=== HunyuanVideo-Foley XXL / Drive kurulumu ==="
test -d /content/drive/MyDrive || { echo "HATA: Önce Google Drive'ı Colab'a bağla."; exit 2; }

mkdir -p "$ROOT/models" "$ROOT/audio/foley" "$ROOT/cache/huggingface" "$WEIGHTS"

if [ ! -d "$APP/.git" ]; then
  git clone https://github.com/Tencent-Hunyuan/HunyuanVideo-Foley.git "$APP"
else
  git -C "$APP" pull --ff-only
fi

# Google Drive mounted filesystem can break Python venv/ensurepip symlinks.
# Keep only code + weights + outputs on Drive; create the disposable runtime env on /content.
rm -rf "$ENV"
python3 -m venv "$ENV" --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py -o /content/get-pip.py
"$ENV/bin/python" /content/get-pip.py
"$ENV/bin/python" -m pip install -U pip setuptools wheel
"$ENV/bin/pip" install -r "$APP/requirements.txt"
"$ENV/bin/pip" install -U huggingface_hub

export HF_HOME="$ROOT/cache/huggingface"
export HUGGINGFACE_HUB_CACHE="$ROOT/cache/huggingface/hub"

echo
echo "Kod Drive'da: $APP"
echo "XXL ağırlıkları Drive'a inecek: $WEIGHTS"
echo "Runtime env: $ENV"
echo "T4 modu: XXL + --enable_offload (~12 GB VRAM, resmi README)."
echo "tamamlandı"
