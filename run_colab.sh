#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ! -d /content ]]; then
  echo "Bu betik Google Colab için hazırlandı." >&2
  exit 1
fi

python - <<'PY'
from google.colab import drive
drive.mount('/content/drive')
PY

export PROJECT_ROOT="/content/drive/MyDrive/CartoonV1/LTX2"
export HF_HOME="$PROJECT_ROOT/cache/huggingface"
mkdir -p "$PROJECT_ROOT"/{characters,config,models,output,cache,work}

if [[ -z "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN="$(python - <<'PY'
from google.colab import userdata
try:
    print(userdata.get('HF_TOKEN') or '')
except Exception:
    print('')
PY
)"
fi

bash /content/cartoonv1/scripts/install_ltx2.sh
bash /content/cartoonv1/scripts/download_models.sh
python /content/cartoonv1/scripts/generate.py

echo "TAMAMLANDI: $PROJECT_ROOT/output/black_cat_20s.mp4"
