#!/usr/bin/env bash
set -Eeuo pipefail

LTX_REPO="$PROJECT_ROOT/work/LTX-2"
python -m pip install -q -U uv huggingface_hub

if [[ ! -d "$LTX_REPO/.git" ]]; then
  git clone --depth 1 https://github.com/Lightricks/LTX-2.git "$LTX_REPO"
else
  git -C "$LTX_REPO" pull --ff-only
fi

cd "$LTX_REPO"
uv sync --frozen

