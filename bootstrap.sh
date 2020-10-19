################################################################### INSTALL DEPENDENCIES #

#if sudo hwinfo --gfxcard | grep nvidia
#then 
#   sudo apt-get install nvidia-cuda-toolkit
#   sudo zypper addrepo --refresh https://download.nvidia.com/opensuse/tumbleweed NVIDIA
#   sudo zypper install x11-video-nvidiaG05 nvidia-computeG05
#   pip install -U torch torchvision
#   pip install -U tensorflow-gpu
#else
#   echo "NO CUDA-CAPABLE GPU AVAILABLE";
#   pip install -U tensorflow
#   pip install -U torch==1.5.0+cpu torchvision==0.6.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
#fi
sudo apt-get install libssl-dev
sudo zypper install gcc-c++ openssl-devel
sudo pacman -S python-pyopenssl

pip install -U flask
pip install -U SPARQLWrapper
pip install -U gensim
pip install -U spacy
pip install -U folium
pip install -U geopy
pip install -U tensorflow-datasets
pip install -U flask_login
pip install -U pyqrcode
pip install -U bson
pip install -U lmdb
pip install -U hnswlib
pip install -U flask_scrypt
pip install -U flask_mail
pip install -U nltk
pip install -U bs4
pip install -U pymongo
pip install -U symspellpy
pip install -U polyglot
pip install -U flask_wtf
pip install -U polyglot
pip install -U PyICU
pip install -U pycld2
pip install -U werkzeug==0.16.1
pip install -U scrapy
pip install -U tldextract
pip install -U scikit-learn
pip install -U pandas
pip install -U torchvision
pip install -U h5py

python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt')"

chmod +x future.py

echo "All dependencies installed"
echo "Terminate now with CTRL+C if you do not want to train any machine learning model"
read -p "Otherwise, press enter to continue"
##########################################################################################



################################################################### TRAIN THE MODELS #####

sh download_coco_dataset.sh
python image_tagger_build_vocab.py   
python resize_coco_dataset.py
python train_image_captioning.py
python chatbot.py
python translator_esp_eng.py

##########################################################################################



################################################################### TRAIN THE MODELS #####

echo "Building index..."
echo "Terminate at any time with CTRL+C and proceed to execute ./save_index.sh"
echo "The process can be resumed later by running ./build_index.sh again"
chmod +x save_index.sh
chmod +x build_index.sh
./build_index.sh

##########################################################################################

echo "Proceed to execute ./save_index.sh"
echo "And finally start the server with ./future.py"
echo "The process of building the index can be resumed later by running ./build_index.sh again"
