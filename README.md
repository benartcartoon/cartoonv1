# CartoonV1 — WAN2.2

Google Colab + Google Drive üzerinde WAN2.2 TI2V-5B ile karakter görselinden video üretimi.

## Drive
`/content/drive/MyDrive/Wan2.2-Cartoon/`
- models/Wan2.2-TI2V-5B
- characters/
- input/
- output/

## Colab tek hücre
```python
from google.colab import drive
import os
if not os.path.ismount("/content/drive"): drive.mount("/content/drive")
!rm -rf /content/cartoonv1
!git clone -q https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1
!bash /content/cartoonv1/colab/setup_wan22.sh
```

Kurulum bitince Gradio public linki açılır. Arayüzde referans karakter görseli, prompt, kare sayısı, steps ve seed ayarlanabilir. Çıktı Drive/output içine kaydedilir.
