#!/usr/bin/env bash
set -Eeuo pipefail

MODEL_ROOT="$PROJECT_ROOT/models/ltx-2.5"
mkdir -p "$MODEL_ROOT"

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN bulunamadı. Lightricks/LTX-2.5 model şartlarını Hugging Face'te kabul edin," >&2
  echo "Colab Secrets bölümüne HF_TOKEN adlı Read token ekleyip yeniden çalıştırın." >&2
  exit 2
fi

python - <<'PY'
import os
from huggingface_hub import login, snapshot_download

root = os.path.join(os.environ["PROJECT_ROOT"], "models", "ltx-2.5")
login(token=os.environ["HF_TOKEN"], add_to_git_credential=False)
snapshot_download(
    repo_id="Lightricks/LTX-2.5",
    local_dir=root,
    allow_patterns=[
        "diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors",
        "text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors",
        "vae/ltx-2.5-video-vae-conv-bf16.safetensors",
        "vae/ltx-2.5-audio-vae-bf16.safetensors",
        "latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors",
    ],
)
print("MODEL TAMAMLANDI:", root)
PY

