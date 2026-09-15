#!/usr/bin/env python3
import argparse
import hashlib
import subprocess
from pathlib import Path
import yaml


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def character_prompt(character):
    fixed = character.get("appearance", "").strip()
    never = ", ".join(character.get("never_change", []))
    return f"{fixed}. Keep exactly the same identity and appearance. Locked traits: {never}."


def stable_seed(text):
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def run(cmd, cwd=None):
    print("CALISIYOR:", " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), cwd=cwd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--story", required=True)
    ap.add_argument("--characters", required=True)
    args = ap.parse_args()

    config = load_yaml(args.config)
    story = load_yaml(args.story)
    chars = load_yaml(args.characters)["characters"]
    drive = Path(config["drive_root"])
    scenes_dir = drive / "scenes"
    output_dir = drive / "output"
    temp_dir = drive / "temp"
    for p in [scenes_dir, output_dir, temp_dir, drive/"cache", drive/"characters"]:
        p.mkdir(parents=True, exist_ok=True)

    wan = config["wan"]
    wan_code = Path(wan["code_dir"])
    model_dir = Path(wan["model_dir"])
    required = ["config.json", "diffusion_pytorch_model.safetensors", "models_t5_umt5-xxl-enc-bf16.pth", "Wan2.1_VAE.pth"]
    missing = [x for x in required if not (model_dir/x).is_file()]
    if missing:
        raise SystemExit("HATA: Eksik Wan dosyalari: " + ", ".join(missing))
    if not (wan_code/"generate.py").is_file():
        raise SystemExit(f"HATA: Wan2.1 kodu bulunamadi: {wan_code}")

    scenes = story.get("scenes", [])
    if not scenes:
        raise SystemExit("HATA: story.yaml icinde sahne yok.")
    if config["video"].get("test_mode", True):
        limit = int(config["video"].get("test_seconds", 5))
        chosen=[]; total=0
        for s in scenes:
            if total >= limit: break
            chosen.append(s); total += int(s.get("duration", 5))
        scenes=chosen

    print(f"Proje: {config['project_name']} | Sahne: {len(scenes)} | Model: {wan['model_id']}", flush=True)
    made=[]
    for index, scene in enumerate(scenes, 1):
        sid=str(scene.get("id", index))
        out=scenes_dir/f"scene_{sid}.mp4"
        made.append(out)
        if out.exists() and out.stat().st_size > 100000:
            print(f"[{index}/{len(scenes)}] SAHNE {sid} zaten hazir -> ATLANDI", flush=True)
            continue
        locked=[]
        for cid in scene.get("characters", []):
            if cid not in chars: raise SystemExit(f"HATA: Bilinmeyen karakter: {cid}")
            locked.append(character_prompt(chars[cid]))
        prompt=" ".join(locked + [
            f"Location: {scene.get('location','')}", f"Action: {scene.get('action','')}",
            f"Camera: {scene.get('camera','')}",
            "high quality family-friendly animated cartoon, consistent art style, stable character identity, no redesign"
        ])
        seed=stable_seed("|".join(scene.get("characters", [])) + "|CartoonV1")
        print(f"[{index}/{len(scenes)}] SAHNE {sid} uretiliyor...", flush=True)
        cmd=[
            "python3", "generate.py", "--task", wan["task"], "--size", wan["size"],
            "--ckpt_dir", str(model_dir), "--offload_model", str(wan.get("offload_model", True)),
            "--sample_shift", str(wan.get("sample_shift",8)),
            "--sample_guide_scale", str(wan.get("sample_guide_scale",6)),
            "--frame_num", str(wan.get("frame_num",81)), "--base_seed", str(seed),
            "--prompt", prompt, "--save_file", str(out)
        ]
        if wan.get("t5_cpu", False):
            cmd.append("--t5_cpu")
        run(cmd, cwd=wan_code)
        if not out.exists(): raise SystemExit(f"HATA: Sahne olusmadi: {out}")

    concat=temp_dir/"concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in made), encoding="utf-8")
    final=output_dir/config["output"].get("final_name","cartoon_final.mp4")
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(final)])
    print(f"\nHAZIR: {final}", flush=True)

if __name__ == "__main__":
    main()
