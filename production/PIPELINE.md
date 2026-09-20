# Profesyonel üretim zinciri

1. Konu + toplam süre alınır.
2. Süre 5 saniyelik shot'lara otomatik bölünür.
3. Her shot onaylı karakter ve dünya referanslarını zorunlu kullanır.
4. WAN2.2 her shot'ı ayrı üretir.
5. QC kapısı: ekstra/eksik uzuv, göz kayması, yüz/kimlik/renk sapması, duplicate karakter, prop/environment continuity hatası -> RED -> yeniden üretim (maksimum 3 deneme).
6. Görünen hareketlerden timecode'lu diegetic SFX planı çıkarılır. Diyalog varsa lip-sync zorunludur. Müzik isteğe bağlı/düşük seviyededir.
7. Tüm shot'lar PASS olmadan final birleştirme başlamaz.
8. Shot'lar sırayla birleştirilir.
9. Final 1920x1080 ve 60 FPS'e dönüştürülür.
10. Final QC sonrası Drive output'a yazılır.

## Güvenli tasarım
Pipeline QC yapılmadığını başarı saymaz. Her shot için `shot_XX.mp4.qc.json` gerekir:
```json
{"pass": true, "reasons": []}
```
Otomatik görsel QC modeli bağlandığında aynı sözleşmeyi kullanır.
