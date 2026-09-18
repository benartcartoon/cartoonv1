# CartoonV1 — LTX-2.5

Bu depo, Google Colab GPU ile LTX-2.5 kullanarak sabit bir karakter görselinden çizgi film videosu üretir.

## Tek komut

Colab'da GPU'yu açın, sonra yalnızca:

```bash
!git clone -q https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1 && bash /content/cartoonv1/run_colab.sh
```

İlk çalıştırmada Google Drive bağlanır, LTX-2.5 kodu kurulur ve yaklaşık 66 GiB model dosyası Drive'a bir kez indirilir. Sonraki çalıştırmalar aynı modeli Drive'dan kullanır.

## Drive düzeni

```
MyDrive/CartoonV1/LTX2/
├── characters/black_cat_hat.png
├── config/story.txt
├── models/ltx-2.5/
└── output/
```

## İlk deneme

Varsayılan senaryo iki adet yaklaşık 10 saniyelik sahne üretir ve bunları 20 saniyelik tek MP4 olarak birleştirir: siyah şapkalı kedi selam verir, kameraya bakar, dans eder ve kadrajdan çıkar.

> LTX-2.5 ağır bir modeldir. T4 15 GB için FP8 ve disk offload açıktır; çalışma yavaş olabilir. Daha güçlü GPU varsa `OFFLOAD=cpu` kullanılabilir.

