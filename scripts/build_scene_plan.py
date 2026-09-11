from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]
settings = json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8"))
characters_cfg = json.loads((ROOT / settings["character_config"]).read_text(encoding="utf-8"))
topic = (ROOT / settings["topic_file"]).read_text(encoding="utf-8").strip()

scene_seconds = int(settings["scene_seconds"])
total_seconds = int(settings["target_minutes"] * 60)
scene_count = math.ceil(total_seconds / scene_seconds)

character_ids = [c["id"] for c in characters_cfg["characters"]]

scenes = []
for i in range(scene_count):
    scenes.append({
        "scene": i + 1,
        "duration_seconds": scene_seconds,
        "topic": topic,
        "characters": character_ids,
        "prompt": f"3D animated family-friendly cartoon scene. Story topic: {topic}. Keep recurring characters visually consistent with their reference images. Scene {i + 1} of {scene_count}.",
        "negative_prompt": "text, captions, watermark, logo, duplicate character, extra limbs, deformed face, inconsistent costume"
    })

out_dir = ROOT / settings["output_dir"]
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "scene_plan.json"
out_file.write_text(json.dumps({"topic": topic, "scene_count": scene_count, "scenes": scenes}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Scene plan created: {out_file}")
print(f"Scenes: {scene_count} x {scene_seconds}s ≈ {scene_count * scene_seconds / 60:.1f} min")
