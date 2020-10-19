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
sudo apt-get install libssl-dev python3-icu
sudo zypper install gcc-c++ openssl-devel
sudo pacman -S python-pyopenssl

pip3 install -U flask
pip3 install -U SPARQLWrapper
pip3 install -U gensim
pip3 install -U spacy
pip3 install -U folium
pip3 install -U geopy
pip3 install -U tensorflow-datasets
pip3 install -U flask_login
pip3 install -U pyqrcode
pip3 install -U bson
pip3 install -U lmdb
pip3 install -U hnswlib
pip3 install -U flask_scrypt
pip3 install -U flask_mail
pip3 install -U nltk
pip3 install -U bs4
pip3 install -U pymongo
pip3 install -U symspellpy
pip3 install -U polyglot
pip3 install -U flask_wtf
pip3 install -U polyglot
pip3 install -U PyICU
pip3 install -U pycld2
pip3 install -U werkzeug==0.16.1
pip3 install -U scrapy
pip3 install -U tldextract
pip3 install -U scikit-learn
pip3 install -U pandas
pip3 install -U torchvision
pip install -U h5py

python3 -m spacy download en_core_web_sm
python3 -c "import nltk; nltk.download('punkt')"

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