# Run this ONE cell in a Colab GPU runtime
from google.colab import drive
drive.mount('/content/drive')
!apt-get -qq update
!apt-get -qq install -y aria2
!rm -rf /content/cartoonv1
!git clone -q https://github.com/benartcartoon/cartoonv1.git /content/cartoonv1
!bash /content/cartoonv1/colab/setup_animatediff.sh
