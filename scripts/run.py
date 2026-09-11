from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
settings = json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8"))
topic = (ROOT / settings["topic_file"]).read_text(encoding="utf-8").strip()
characters = json.loads((ROOT / settings["character_config"]).read_text(encoding="utf-8"))["characters"]

print("=== CARTOONV1 ===")
print(f"Konu: {topic}")
print(f"Hedef süre: {settings['target_minutes']} dakika")
print(f"Karakter sayısı: {len(characters)}")

missing = [c["image"] for c in characters if not (ROOT / c["image"]).exists()]
if missing:
    print("\nEksik karakter görselleri:")
    for item in missing:
        print(" -", item)
    raise SystemExit("Önce karakter PNG dosyalarını characters/images/ klasörüne yükle.")

print("\nHazırlık tamam. Bir sonraki aşamada ComfyUI workflow ve video üretim motoru bu script'e bağlanacak.")
