![Website](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fwearebuildingthefuture.com) ![GitHub](https://img.shields.io/github/license/rtrevinnoc/FUTURE) ![Keybase BTC](https://img.shields.io/keybase/btc/rtrevinnoc)
# FUTURE

![Screenshot_20200517_192300](https://user-images.githubusercontent.com/7103315/82164538-bea0e600-9876-11ea-8d42-c8a1b126d8fb.png)

__FUTURE__ is a search engine that improves on traditional methods of search by keyword by instead relying on machine learning techniques to encode words as vectors, and capture their meaning and be able to return more precise matches, all while dropping user tracking as only the query is sufficient to retrieve meaningful data.
It was written with Python for backend, using Tensorflow and PyTorch and web technologies for the frontend.

*__FUTURE__ IS DISTRIBUTED UNDER THE __GNU GPL v3__*



## INSTRUCTIONS

In order to get FUTURE working, first you will need to install the appropiate tensorflow and pytorch packages for your system. After that, it is only necessary that you run the following commands, which have been tested on Arch Linux, Open SuSe and Ubuntu:

```bash
./bootstrap.sh
```

The last command will never finish in a feasible amount of time, as it is building the index. However it can always be paused with CTRL+C and resumed later. Shell scripts to automate tasks are provided and are aptly named.

Pause the crawler with CTRL+C, and execute:

```bash
./save_index.sh
```


Finally, start the server, and point your browser to 0.0.0.0:3000 with the command below:

```bash
./future.py
```



## HACKING

Out of the box, **FUTURE** is designed as a web search engine, which means that running the `./bootstrap.sh` script provided will only prepare it to search web pages. However, it is hackable down to the core, therefore, you can open `indexer.py` and tinker with it to save other types of data into the *LMDB* database, or perhaps refer to the `Monad` class on the `Monad.py` and write the files to handle the creation of the database and the index yourself.

If you were to modify the data that is saved into the database, you may also need to change how it is served in an HTML template, and for that refer to the lines **240-327** of `future.py`, where you can adapt the code that manages the database to whatever suits your needs.

For further modifications, feel free to fork the project, but bear in mind the terms of the GPL v3 license.



## DEPENDENCIES

Below are listed all the projects upon which __FUTURE__ rests.
Name | License
---|---
[Tensorflow](https://github.com/tensorflow/tensorflow)|Apache 2.0
[Flask](https://github.com/pallets/flask)|BSD 3-Clause
[Flask_login](https://github.com/maxcountryman/flask-login)|MIT                          
[Werkzeug](https://github.com/pallets/werkzeug)|BSD 3-Clause                
[Flask_scrypt](https://github.com/cryptojuice/flask-scrypt)|MIT                       
[Flask_Mail](https://github.com/mattupstate/flask-mail)|BSD License               
[MongoDB](https://github.com/mongodb/mongo)|Server Side Public License   
[MongoDB Python bindings](https://github.com/mongodb/mongo-python-driver)|Apache 2.0                   
[SymSpell](https://github.com/wolfgarbe/SymSpell/)|MIT
[Polyglot](https://github.com/aboSamoor/polyglot/)|GPL v3                   
[Beautifulsoup ](https://code.launchpad.net/beautifulsoup)|BSD 2-Clause              
[BSON Python bindings](https://github.com/py-bson/bson)|Apache 2.0                
[NumPy](https://github.com/numpy/numpy)|BSD 3-Clause     
[GeoPy](https://github.com/geopy/geopy)|MIT                   
[SciKit Learn](https://github.com/scikit-learn/scikit-learn)|BSD 3-Clause                 
[Pandas](https://github.com/pandas-dev/pandas)|BSD 3-Clause     
[PyTorch](https://github.com/pytorch/pytorch)|BSD 3-Clause                  
[Gensim](https://github.com/RaRe-Technologies/gensim)|LGPL 2.1                      
[NLTK](https://github.com/nltk/nltk)|Apache 2.0      
[Scrapy](https://github.com/scrapy/scrapy)|BSD License                   
[H5PY](https://github.com/h5py/h5py)|BSD 3-Clause              
[LMBD](https://github.com/LMDB/lmdb)|OpenLDAP
[LMBD Python bindings](https://github.com/jnwatson/py-lmdb)|OpenLDAP                    
[tldextract](https://github.com/john-kurkowski/tldextract)|BSD 3-Clause       
[Python Imaging Library (PIL)](http://www.pythonware.com/products/pil/)|PIL License             
[COCO API (Python bindings)](https://github.com/cocodataset/cocoapi)|BSD 2-Clause             
[WTForms](https://github.com/wtforms/wtforms)|BSD 3-Clause               
[Flask_wtf](https://github.com/lepture/flask-wtf)|BSD 3-Clause
[HNSWLib](https://github.com/nmslib/hnswlib)|Apache 2.0
[JQuery](https://github.com/jquery/jquery)|MIT                      
[JQuery UI](https://github.com/jquery/jquery-ui)|MIT             
[Particles JS](https://github.com/VincentGarreau/particles.js/)|MIT             
[Simplebar](https://github.com/Grsmto/simplebar)|MIT  
[Ionicons](https://github.com/ionic-team/ionicons)|MIT         
[Source Sans Pro](https://github.com/adobe-fonts/source-sans-pro)|OFL 1.1                   
[GloVe](https://github.com/stanfordnlp/GloVe)|Apache 2.0
[SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper)|W3C License      
[TextScrambler](https://codepen.io/soulwire/pen/mErPAK)|BSD-like   
[NMT with Attention](https://github.com/tensorflow/docs/blob/master/site/en/tutorials/text/nmt_with_attention.ipynb)|Apache 2.0
[Transformer Chatbot](https://github.com/tensorflow/examples/blob/master/community/en/transformer_chatbot.ipynb)|Apache 2.0
[Image Captioning](https://github.com/yunjey/pytorch-tutorial/tree/master/tutorials/03-advanced/)|MIT

### FUTURE on w3m
[![asciicast](https://asciinema.org/a/331246.svg)](https://asciinema.org/a/331246?autoplay=1)
