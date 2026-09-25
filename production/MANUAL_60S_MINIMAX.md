# MiniMax-H3 15 saniyelik parca plani

Hedef: kullanici ComfyUI'de prompt ve ilk referanslari elle girer. Her parca 15 saniyedir.

## 1 dakikalik video
- part_01: ilk referanslar + kullanici promptu
- part_02: part_01 son karesi + sabit karakter referanslari + ayni/devam promptu
- part_03: part_02 son karesi + sabit karakter referanslari + ayni/devam promptu
- part_04: part_03 son karesi + sabit karakter referanslari + ayni/devam promptu
- final: 4 x 15 saniye birlestirilir.

## MiniMax H3
24 fps'te 15 saniye icin 362 civari frame kullanilir. MiniMaxH3ReferenceToVideo node'unun egitim araligi yaklasik 124-362 frame'dir.

## Drive
Root: /content/drive/MyDrive/MiniMax-H3
Parcalar: /content/drive/MyDrive/MiniMax-H3/manual_60s/parts
Son kareler: /content/drive/MyDrive/MiniMax-H3/manual_60s/frames
Final: /content/drive/MyDrive/MiniMax-H3/manual_60s/final/final_60s.mp4

Not: Otomatik zincirin API workflow'u, kullanicinin ComfyUI'de basarili bir 15 saniyelik workflow'u API JSON olarak kaydetmesiyle sabitlenecek. Bu, kullanicinin secmis oldugu node/LoRA/sampler ayarlarini tahmin etmeden aynen korumak icindir.
