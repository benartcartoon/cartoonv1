from google.colab import drive
import os
if not os.path.ismount("/content/drive"):
    drive.mount("/content/drive")
!rm -rf /content/cartoonv1
!git clone -q https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1
!bash /content/cartoonv1/colab/setup_wan22.sh
