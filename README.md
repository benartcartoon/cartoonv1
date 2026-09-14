# CartoonV1

Wan2 tabanli, ayni karakterleri koruyarak uzun cizgi film uretmek icin Colab + Google Drive + GitHub projesi.

## Mimari
- GitHub: kod, senaryo, karakter tanimlari, ayarlar
- Google Drive: buyuk modeller, karakter referans gorselleri, ara klipler ve final videolar
- Colab: sadece GPU ile uretim

## Hedef akis
1. `story/story.yaml` okunur.
2. `characters/characters.yaml` ile sabit karakter kimlikleri eklenir.
3. Senaryo kisa sahnelere bolunur.
4. Wan2 her sahneyi ayni karakter referanslariyla uretir.
5. Klipler birlestirilir ve final MP4 Drive'a yazilir.

## Google Drive yapisi
`/MyDrive/CartoonV1/`
- `models/` buyuk Wan2 dosyalari
- `characters/` referans gorseller
- `cache/` model/cache
- `scenes/` uretilen sahneler
- `output/` final videolar

## Colab tek hucre
```python
from google.colab import drive
drive.mount('/content/drive')

!rm -rf /content/cartoonv1
!git clone -q https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1
!bash /content/cartoonv1/oneclick.sh
```

Ilk test 30-60 saniye olacak. Karakter tutarliligi onaylandiktan sonra hedef sure 10 dakikaya acilacak.
