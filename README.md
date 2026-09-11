# cartoonv1

Sabit karakterlerle tekrar kullanılabilen çizgi film/video üretim projesi.

## Kullanım mantığı

1. Karakter PNG dosyaları bir kez `characters/images/` klasörüne eklenir.
2. Yeni bölüm için yalnızca `video_topic.txt` değiştirilir.
3. GPU instance açılır ve repo klonlanır.
4. `install.sh` ortamı hazırlar.
5. `start.sh` üretim sürecini başlatır.
6. Çıktılar `outputs/` klasörüne alınır.
7. Videolar indirildikten sonra geçici GPU instance destroy edilebilir.

## Sabit karakter dosyaları

- `characters/images/kedi.png`
- `characters/images/anne.png`
- `characters/images/baba.png`
- `characters/images/arkadas1.png`
- `characters/images/arkadas2.png`
- `characters/images/kotu_karakter.png`

## Durum

Temel otomasyon iskeleti hazır. ComfyUI video workflow'u ve kullanılacak model(ler) GPU'yu ilk kez açmadan önce/ilk test sırasında eklenecek.
