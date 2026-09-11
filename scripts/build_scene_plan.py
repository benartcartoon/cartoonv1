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

characters = characters_cfg["characters"]
character_ids = [c["id"] for c in characters]
character_names = {c["id"]: c["name"] for c in characters}

story_beats = [
    "opening and discovery",
    "the goal becomes clear",
    "the group starts the journey",
    "a funny obstacle appears",
    "the friends cooperate",
    "a clue changes the direction",
    "the villain creates a problem",
    "the heroes recover and continue",
    "the mystery becomes more exciting",
    "a difficult challenge must be solved",
    "the team uses courage and friendship",
    "the villain is confronted",
    "the final clue is discovered",
    "the goal is reached",
    "warm and satisfying ending"
]

scenes = []
for i in range(scene_count):
    primary = character_ids[i % len(character_ids)]
    secondary = character_ids[(i + 1) % len(character_ids)]
    beat_index = min(len(story_beats) - 1, int(i * len(story_beats) / max(1, scene_count)))
    beat = story_beats[beat_index]
    scene_no = i + 1

    prompt = (
        "High quality family-friendly 3D animated cartoon film, cinematic lighting, detailed environment, "
        "smooth natural motion, expressive faces, consistent character design. "
        f"Story topic: {topic}. Story beat: {beat}. "
        f"Scene {scene_no} of {scene_count}. Main focus character: {character_names[primary]}. "
        f"Supporting character: {character_names[secondary]}. "
        "Preserve the exact colors, clothing, face shape and visual identity of the supplied character reference. "
        "No text on screen. Dynamic camera composition, clear readable action, child-friendly storytelling."
    )

    scenes.append({
        "scene": scene_no,
        "duration_seconds": scene_seconds,
        "topic": topic,
        "story_beat": beat,
        "primary_character": primary,
        "characters": [primary, secondary],
        "prompt": prompt,
        "negative_prompt": (
            "text, captions, subtitles, watermark, logo, duplicate character, extra limbs, extra fingers, "
            "deformed face, inconsistent costume, identity change, flicker, blur, low quality, static frame"
        )
    })

out_dir = ROOT / settings["output_dir"]
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "scene_plan.json"
out_file.write_text(
    json.dumps({"topic": topic, "scene_count": scene_count, "scenes": scenes}, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"Scene plan created: {out_file}")
print(f"Scenes: {scene_count} x {scene_seconds}s ≈ {scene_count * scene_seconds / 60:.1f} min")
