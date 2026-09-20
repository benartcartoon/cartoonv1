# Çizgi Film Yönetmen Kuralları

## Değişmezler
- Karakter kimliği asla değişmez: Miyav, Çanta, Damlacık, Pofu, Yaprak.
- Referans görseli olmayan karakter üretime girmez.
- Ev, oda düzeni ve temel eşyalar world bible referanslarına bağlı kalır.
- Ana üretim birimi 5 saniyedir. İstenen toplam süre 5 saniyelik shot'lara bölünür.

## Görsel kalite kapısı
Reddedilecek hatalar: ekstra kol/bacak/ayak/parmak/kuyruk, eksik uzuv, birleşmiş uzuv, çift yüz/göz, göz kayması, yüz deformasyonu, karakter kopyalanması, renk/kıyafet/aksesuar sapması, ani ölçek değişimi, arka plan/eşya continuity hatası.
Hatalı shot final videoya alınmaz; yeniden üretilir.

## Shot continuity
Her shot: start_state, action, end_state, camera, character_refs, environment_ref, negative_prompt içerir. Bir shot'ın end_state'i sonraki shot'ın start_state'ine aktarılır.

## Ses yönetimi
Müzik ana ses değildir. Görünen hareketler timecode'lu diegetic SFX üretir: adım, sprey, bez, kapı, çarpma, zıplama, eşya vb. Konuşma varsa ağız hareketi/lip-sync ile eşleştirilir. Müzik isteğe bağlı ve düşük seviyededir.

## Final
Shot QC -> hatalı shot retry -> SFX/diyalog senkron -> birleştirme -> 1080p upscale -> 60 FPS -> final QC.
