#!/usr/bin/env python3
import argparse
from pathlib import Path
import yaml


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def character_prompt(character):
    fixed = character.get("appearance", "").strip()
    never = ", ".join(character.get("never_change", []))
    return f"{fixed}. Keep exactly the same identity and appearance. Locked traits: {never}."


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
    for name in ["models", "characters", "cache", "scenes", "output"]:
        (drive / name).mkdir(parents=True, exist_ok=True)

    scenes = story.get("scenes", [])
    if not scenes:
        raise SystemExit("HATA: story.yaml icinde sahne yok.")

    print(f"Proje: {config['project_name']}")
    print(f"Senaryo: {story.get('title', '-')}")
    print(f"Sahne sayisi: {len(scenes)}")
    print(f"Drive: {drive}")

    for scene in scenes:
        scene_chars = scene.get("characters", [])
        locked = []
        for cid in scene_chars:
            if cid not in chars:
                raise SystemExit(f"HATA: Bilinmeyen karakter: {cid}")
            locked.append(character_prompt(chars[cid]))
        prompt = " ".join(locked + [
            f"Location: {scene.get('location','')}",
            f"Action: {scene.get('action','')}",
            f"Camera: {scene.get('camera','')}",
            "consistent cartoon style, stable character identity, no character redesign"
        ])
        print(f"\nSAHNE {scene['id']} ({scene.get('duration',5)} sn)")
        print(prompt)

    model_id = config.get("wan", {}).get("model_id", "AUTO_T4")
    if model_id == "AUTO_T4":
        print("\nHAZIRLIK TAMAM. Sonraki adim: T4 icin kullanacagimiz Wan2 modelini sabitleyip gercek video uretimini baglamak.")
    else:
        print(f"\nWan modeli: {model_id}")


if __name__ == "__main__":
    main()
