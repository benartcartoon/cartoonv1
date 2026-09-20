import json, os
from pathlib import Path

ROOT = Path(os.environ.get("CARTOON_DRIVE_ROOT", "/content/drive/MyDrive/Çizgi Film YouTube 1"))
OUT = ROOT / "audio"
CONFIG = Path(__file__).resolve().parents[1] / "config" / "sound_profiles.json"

PROMPTS = {
 "miyav/meow_normal.wav": "cute young orange kitten, one short natural gentle meow, clean isolated sound, no music, no speech",
 "miyav/meow_happy.wav": "same cute young kitten voice identity, happy playful short meow, isolated, no music, no speech",
 "miyav/meow_surprised.wav": "same cute young kitten voice identity, tiny surprised meow, isolated, no music, no speech",
 "yaprak/meow_normal.wav": "cute young female gray and white kitten, soft distinct short meow, isolated, no music, no speech",
 "yaprak/meow_happy.wav": "same gray and white kitten voice identity, happy soft meow, isolated, no music, no speech",
 "yaprak/meow_surprised.wav": "same gray and white kitten voice identity, surprised soft meow, isolated, no music, no speech",
 "pofu/bark_normal.wav": "cute small puppy, one short gentle bark, isolated, no music, no human speech",
 "pofu/bark_happy.wav": "same small puppy voice identity, happy playful short bark, isolated, no music, no human speech",
 "pofu/whimper.wav": "same small puppy voice identity, very short cute gentle whimper, isolated, no music, no human speech",
 "damlacik/happy_water.wav": "tiny cheerful magical water droplet sound, bubbly plop, isolated, no voice, no music",
 "damlacik/surprised_water.wav": "tiny surprised water droplet plop and splash, isolated, no voice, no music",
 "damlacik/water_move.wav": "small clean water swish movement, isolated sound effect, no voice, no music",
 "sfx/spray/spray_01.wav": "three short household spray bottle squirts, clean isolated sound, no music",
 "sfx/cloth_wipe/wipe_01.wav": "soft cloth wiping a clean wooden floor back and forth, isolated sound, no music",
 "sfx/footsteps/wood_small_01.wav": "tiny cartoon character footsteps on wooden floor, isolated, no music",
 "sfx/sparkle/sparkle_01.wav": "short bright magical clean sparkle chime, isolated, no music"
}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = OUT / "sound_generation_manifest.json"
    manifest.write_text(json.dumps(PROMPTS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sound manifest ready: {manifest}")
    print("IMPORTANT: approved WAV files become locked master assets; later episodes reuse them.")
    print("Çanta has no character voice. Physical movement SFX only.")
    print("tamamlandı")

if __name__ == "__main__":
    main()
