################################################################### INSTALL DEPENDENCIES #

#if sudo hwinfo --gfxcard | grep nvidia
#then 
	#sudo apt-get install nvidia-cuda-toolkit
	#sudo zypper addrepo --refresh https://download.nvidia.com/opensuse/tumbleweed NVIDIA
	#sudo zypper install x11-video-nvidiaG05 nvidia-computeG05
	## pip install -U torch torchvision
	#pip install -U tensorflow-gpu
#else
	#echo "NO CUDA-CAPABLE GPU AVAILABLE";
	##pip3 install -U tensorflow
	## pip install -U torch==1.5.0+cpu torchvision==0.6.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
#fi

sudo apt-get install -y libssl-dev python3-icu libicu-dev wget
sudo zypper install gcc-c++ openssl-devel wget
sudo pacman -S python-pyopenssl wget

pip3 install -U PyICU
pip3 install -U pybind11
pip3 install -U pycld2
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
pip3 install -U werkzeug==0.16.1
pip3 install -U scrapy
pip3 install -U tldextract
pip3 install -U scikit-learn
pip3 install -U pandas
# pip3 install -U torchvision
pip3 install -U h5py

python3 -m spacy download en_core_web_sm
python3 -c "import nltk; nltk.download('punkt')"

wget http://nlp.stanford.edu/data/glove.6B.zip
unzip -d "glove.6B" glove.6B.zip
rm -rf glove.6B/glove.6B.100d.txt glove.6B/glove.6B.200d.txt glove.6B/glove.6B.300d.txt
GLOVE_SIZE=$(du glove.6B/glove.6B.50d.txt | cut -f1)

if [ "$GLOVE_SIZE" -gt "167336" ]
then
	sed -i '1i 400000 50' glove.6B/glove.6B.50d.txt
fi

chmod +x future.py
chmod +x save_index.sh
chmod +x build_index.sh

echo "All dependencies installed. You can now proceed to build the index with <<build_index.sh>> and later pause the process with <<save_index.sh>>. Run FUTURE with <<python3 future.py>>"
# echo "Terminate now with CTRL+C if you do not want to train any machine learning model"
# read -p "Otherwise, press enter to continue"

################################################################### TRAIN THE MODELS #####

# python3 chatbot.py
# python3 translator_esp_eng.py

################################################################### TRAIN THE MODELS #####

# echo "Building index..."
# echo "Terminate at any time with CTRL+C and proceed to execute ./save_index.sh"
# echo "The process can be resumed later by running ./build_index.sh again"
# chmod +x save_index.sh
# chmod +x build_index.sh
# ./build_index.sh

##########################################################################################

# echo "Proceed to execute ./save_index.sh"
# echo "And finally start the server with ./future.py"
# echo "The process of building the index can be resumed later by running ./build_index.sh again"
