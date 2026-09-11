from __future__ import annotations

import argparse
import json
import random
import shutil
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8"))
COMFY_URL = SETTINGS["comfyui_url"].rstrip("/")
COMFY_DIR = Path.home() / "ComfyUI"
INPUT_DIR = COMFY_DIR / "input"
OUT_DIR = ROOT / SETTINGS["output_dir"] / "scenes"


def wait_for_comfy(timeout: int = 180) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
            if r.ok:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise RuntimeError("ComfyUI API hazır olmadı.")


def make_prompt(scene: dict, input_name: str, seed: int) -> dict:
    width = int(SETTINGS["generation_width"])
    height = int(SETTINGS["generation_height"])
    fps = int(SETTINGS["generation_fps"])
    seconds = int(scene["duration_seconds"])
    # Wan video length works best with 4n+1 frame counts.
    raw_frames = max(17, fps * seconds)
    length = raw_frames - ((raw_frames - 1) % 4)

    return {
        "37": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": SETTINGS["video_model"],
                "weight_dtype": "default"
            }
        },
        "38": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": SETTINGS["text_encoder"],
                "type": "wan",
                "device": "default"
            }
        },
        "39": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": SETTINGS["vae_model"]}
        },
        "48": {
            "class_type": "ModelSamplingSD3",
            "inputs": {"model": ["37", 0], "shift": 8.0}
        },
        "57": {
            "class_type": "LoadImage",
            "inputs": {"image": input_name}
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["38", 0], "text": scene["prompt"]}
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["38", 0], "text": scene["negative_prompt"]}
        },
        "55": {
            "class_type": "Wan22ImageToVideoLatent",
            "inputs": {
                "vae": ["39", 0],
                "start_image": ["57", 0],
                "width": width,
                "height": height,
                "length": length,
                "batch_size": 1
            }
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["48", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["55", 0],
                "seed": seed,
                "steps": 30,
                "cfg": 5.0,
                "sampler_name": "uni_pc",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["39", 0]}
        },
        "47": {
            "class_type": "SaveWEBM",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": f"cartoonv1_scene_{int(scene['scene']):03d}",
                "codec": "vp9",
                "fps": fps,
                "crf": 16
            }
        }
    }


def queue(prompt: dict) -> str:
    r = requests.post(f"{COMFY_URL}/prompt", json={"prompt": prompt}, timeout=30)
    if not r.ok:
        raise RuntimeError(f"ComfyUI prompt hatası: {r.status_code} {r.text[:1000]}")
    return r.json()["prompt_id"]


def wait_history(prompt_id: str, timeout: int = 3600) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=30)
        r.raise_for_status()
        data = r.json()
        if prompt_id in data:
            item = data[prompt_id]
            status = item.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI üretim hatası: {json.dumps(status, ensure_ascii=False)}")
            if item.get("outputs"):
                return item
        time.sleep(3)
    raise TimeoutError(f"Sahne zaman aşımı: {prompt_id}")


def locate_output(history: dict) -> Path:
    for node in history.get("outputs", {}).values():
        for key in ("videos", "gifs", "images"):
            for obj in node.get(key, []):
                filename = obj.get("filename")
                if not filename:
                    continue
                subfolder = obj.get("subfolder", "")
                candidate = COMFY_DIR / "output" / subfolder / filename
                if candidate.exists():
                    return candidate
    raise FileNotFoundError("ComfyUI çıktı dosyası bulunamadı.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Sadece ilk N sahneyi üret (test için).")
    args = parser.parse_args()

    wait_for_comfy()
    plan_path = ROOT / SETTINGS["output_dir"] / "scene_plan.json"
    if not plan_path.exists():
        raise SystemExit("scene_plan.json yok. Önce build_scene_plan.py çalıştır.")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    char_cfg = json.loads((ROOT / SETTINGS["character_config"]).read_text(encoding="utf-8"))
    chars = {c["id"]: c for c in char_cfg["characters"]}
    scenes = plan["scenes"][: args.limit or None]

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for scene in scenes:
        scene_no = int(scene["scene"])
        primary = scene.get("primary_character") or scene["characters"][0]
        char = chars[primary]
        source = ROOT / char["image"]
        if not source.exists():
            raise FileNotFoundError(source)

        input_name = f"cartoonv1_{primary}.png"
        shutil.copy2(source, INPUT_DIR / input_name)

        print(f"[{scene_no}/{len(scenes)}] {char['name']} sahnesi üretiliyor...")
        prompt = make_prompt(scene, input_name, random.SystemRandom().randint(1, 2**53 - 1))
        prompt_id = queue(prompt)
        history = wait_history(prompt_id)
        generated = locate_output(history)
        target = OUT_DIR / f"scene_{scene_no:03d}{generated.suffix.lower()}"
        shutil.copy2(generated, target)
        print(f"  -> {target}")

    print("Sahne üretimi tamamlandı.")


if __name__ == "__main__":
    main()
