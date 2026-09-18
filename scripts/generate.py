from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(os.environ["PROJECT_ROOT"])
LTX = ROOT / "work" / "LTX-2"
MODEL = ROOT / "models" / "ltx-2.5"
CHARACTER = ROOT / "characters" / "black_cat_hat.png"
STORY = ROOT / "config" / "story.txt"
OUTPUT = ROOT / "output"
UV = ["uv", "run", "python", "-m", "ltx_pipelines.distilled"]

DEFAULT_SCENES = [
    "A cute small black cartoon cat wearing a warm red newsboy cap stands in a bright simple playroom. The cat smiles, raises one paw and slowly waves hello to its friends, then turns its large amber eyes directly toward the camera. The character design remains exactly consistent with the reference image. Smooth child-friendly 3D animation, stable camera, soft warm light, clean background, gentle cheerful ambience.",
    "The same cute black cat in the same warm red newsboy cap looks at the camera, performs a playful simple dance with two side steps and a happy spin, then waves once more and slowly walks out of frame to the right. Keep the face, fur, proportions, amber eyes and red cap identical to the reference. Smooth child-friendly 3D animation, stable camera, soft warm light, cheerful music and tiny paw-step sounds.",
]


def run(command: list[str]) -> None:
    print("+", shlex.join(command), flush=True)
    subprocess.run(command, cwd=LTX, check=True)


def main() -> None:
    if not CHARACTER.exists():
        raise FileNotFoundError(f"Karakter görseli bulunamadı: {CHARACTER}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    if STORY.exists():
        scenes = [s.strip() for s in STORY.read_text(encoding="utf-8").split("---") if s.strip()]
    else:
        STORY.parent.mkdir(parents=True, exist_ok=True)
        STORY.write_text("\n---\n".join(DEFAULT_SCENES), encoding="utf-8")
        scenes = DEFAULT_SCENES

    common = [
        *UV,
        "--transformer-path", str(MODEL / "diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors"),
        "--text-encoder-path", str(MODEL / "text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors"),
        "--video-vae-path", str(MODEL / "vae/ltx-2.5-video-vae-conv-bf16.safetensors"),
        "--audio-vae-path", str(MODEL / "vae/ltx-2.5-audio-vae-bf16.safetensors"),
        "--spatial-upsampler-path", str(MODEL / "latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors"),
        "--height", os.getenv("HEIGHT", "512"),
        "--width", os.getenv("WIDTH", "768"),
        "--frame-rate", os.getenv("FPS", "24"),
        "--num-frames", os.getenv("FRAMES_PER_SCENE", "241"),
        "--offload", os.getenv("OFFLOAD", "disk"),
        "--image", str(CHARACTER), "0", "0.95",
    ]
    gpu_capability = subprocess.run(
        ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
        check=False, capture_output=True, text=True,
    ).stdout.strip()
    try:
        major, minor = (int(x) for x in gpu_capability.split(".", 1))
    except (ValueError, TypeError):
        major, minor = (0, 0)
    if (major, minor) >= (8, 9):
        common += ["--quantization", "fp8-cast"]
    else:
        print(f"GPU compute capability {gpu_capability or 'bilinmiyor'}: FP8 kapalı, disk offload kullanılacak.")

    clips: list[Path] = []
    for index, prompt in enumerate(scenes, start=1):
        clip = OUTPUT / f"scene_{index:02d}.mp4"
        run([*common, "--seed", str(4200 + index), "--prompt", prompt, "--output-path", str(clip)])
        clips.append(clip)

    concat = ROOT / "work" / "concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    final = OUTPUT / "black_cat_20s.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(final)])
    print(f"TAMAMLANDI: {final}")


if __name__ == "__main__":
    main()
