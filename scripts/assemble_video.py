from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8"))
SCENE_DIR = ROOT / SETTINGS["output_dir"] / "scenes"
OUT_DIR = ROOT / SETTINGS["output_dir"]


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    scenes = sorted(SCENE_DIR.glob("scene_*.*"))
    scenes = [p for p in scenes if p.suffix.lower() in {".webm", ".mp4", ".mov", ".mkv"}]
    if not scenes:
        raise SystemExit("Birleştirilecek sahne bulunamadı.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    concat_file = OUT_DIR / "concat.txt"
    concat_file.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in scenes) + "\n", encoding="utf-8")

    joined = OUT_DIR / "joined.webm"
    try:
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(joined)])
    except subprocess.CalledProcessError:
        joined = OUT_DIR / "joined_reencoded.mp4"
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(joined)
        ])

    final = OUT_DIR / "cartoonv1_final_1080p60.mp4"
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    )
    run([
        "ffmpeg", "-y", "-i", str(joined),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", str(SETTINGS.get("final_crf", 16)),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(final)
    ])
    print(f"Final video hazır: {final}")


if __name__ == "__main__":
    main()
