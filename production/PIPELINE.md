# Miyav Cartoon — 10 Dakikalık Otomatik Üretim Zinciri

1. Colab'da tek başlangıç hücresi çalıştırılır.
2. Drive'daki `MiniMax-H3/characters` klasörü sabit karakter kütüphanesidir.
3. Bölüm hedefi 600 saniyedir ve 15 saniyelik 40 sahneye bölünür.
4. Her sahne için gerekli karakter referansları `characters.json` üzerinden otomatik seçilir.
5. Sahne 1 ana referanslarla başlar. Sahne N>1 için önceki PASS sahnesinin son karesi continuity referansı olarak çıkarılır ve gerekli sabit karakter referanslarıyla birlikte kullanılır.
6. Her sahne tamamlanır tamamlanmaz Drive'a atomik olarak kaydedilir; `state.json` güncellenir.
7. Bir sahne hata verirse önceki başarılı sahneler korunur; aynı sahne yeniden denenir. Varsayılan maksimum deneme 3'tür.
8. Colab koparsa yeniden başlatıldığında `state.json` ve mevcut PASS dosyaları okunur; ilk eksik/başarısız sahneden devam edilir.
9. Karakter görünümü, kişiliği ve voice_id kilitlidir. İnsan konuşması yoktur.
10. 40 sahnenin tamamı PASS olmadan final birleştirme yapılmaz.
11. Final yaklaşık 10 dakika, 1920x1080, 60 FPS olarak Drive'a yazılır.

## Drive düzeni
`MiniMax-H3/characters/` sabit referanslar.
`MiniMax-H3/episodes/episode_001/plan.json` 40 sahnelik plan.
`.../shots/shot_001.mp4` ... `shot_040.mp4`.
`.../frames/shot_001_last.png` continuity kareleri.
`.../state.json` kaldığı yer ve deneme sayıları.
`.../final/episode_001.mp4` final video.

## Prompt kilidi
Her sahne promptuna otomatik olarak karakterin görünüm kilidi + kişilik özellikleri + non-human voice_id eklenir. Bu kurallar sahne metni tarafından geçersiz kılınamaz.
