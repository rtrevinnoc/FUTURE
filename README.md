![Website](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fwearebuildingthefuture.com) [![Documentation Status](https://readthedocs.org/projects/wearebuildingthefuture/badge/?version=latest)](https://wearebuildingthefuture.readthedocs.io/en/latest/?badge=latest) ![GitHub](https://img.shields.io/github/license/rtrevinnoc/FUTURE) ![Keybase BTC](https://img.shields.io/keybase/btc/rtrevinnoc)\
[![Buy Me A Coffee](https://camo.githubusercontent.com/031fc5a134cdca5ae3460822aba371e63f794233/68747470733a2f2f7777772e6275796d6561636f666665652e636f6d2f6173736574732f696d672f637573746f6d5f696d616765732f6f72616e67655f696d672e706e67)](https://www.buymeacoffee.com/searchatfuture)

# FUTURE

![Screenshot_20200517_192300](https://user-images.githubusercontent.com/7103315/82164538-bea0e600-9876-11ea-8d42-c8a1b126d8fb.png)

FUTURE is a completely stand alone, open-source search engine that's focused on privacy and decentralization, so that any user can also self-host their own instance to contribute to a shared index of web pages accessible through any one of them. Given the small index that it currently has, it also works as a meta-search engine, mixing its own results with others from public Searx instances, to be capable of answering any request properly. [Here is a small presentation](https://future-pitch.glitch.me/#0) that serves to show why FUTURE is different, better and how it accomplishes that.

The decentralization aspect of the search engine is a core feature as it allows anyone to expand the index and improve the service, while also increasing reliability by redundancy. Currently the main node is located at https://wearebuildingthefuture.com.

If you are planning to host your own instance, we strongly encourage you to consider using [Uberspace](https://uberspace.de/en/) as they offer an excellent service and instances for a fair price.



## HOW DOES IT WORK?

![Graph](https://cdn.glitch.com/ede86e6d-2c5a-40c6-b1a1-546bb881a618%2Fhow_it_works.png?v=1612302725088)



## DOCUMENTATION

Documentation is available on-line at https://wearebuildingthefuture.readthedocs.io/en/latest/ and in the `docs` directory.

### QUICKSTART

After cloning the repository, add a `config.py` file, which will allow you to customize important parts of your instance without directly modifying the source code and struggling with updates. It is suggested to start with this configuration template, which is essentially equal to the one used for the main instance:

```python
#!/usr/bin/env python3
# -*- coding: utf8 -*-
import secrets

WTF_CSRF_ENABLED = True
SECRET_KEY = secrets.token_urlsafe(16)
HOST_NAME = "my_public_future_instance"         # THE NAMES 'private' and 'wearebuildingthefuture.com' are reserved for private and main nodes, respectively.
with open("tranco_JKGY.csv") as tranco:
        SEED_URLS = [x.strip() for x in tranco.readlines()]
PEER_PORT = 3000
HOME_URL = "wearebuildingthefuture.com"
LIMIT_DOMAINS = None
ALLOWED_DOMAINS = []
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 2.0
CONCURRENT_ITEMS = 100
REACTOR_THREADPOOL_MAXSIZE = 20
DOWNLOAD_MAXSIZE = 10000000
AUTOTHROTTLE = True
TARGET_CONCURRENCY = 2.0
MAX_DELAY = 30.0
START_DELAY = 1.0
DEPTH_PRIORITY = 1
LOG_LEVEL = 'INFO'
CONTACT = "rtrevinnoc@wearebuildingthefuture.com"
MAINTAINER = "Roberto Treviño Cervantes"
FIRST_NOTICE = "Written and Mantained By <a href='https://keybase.io/rtrevinnoc'>Roberto Treviño</a>"
SECOND_NOTICE = "Proudly Hosted on <a href='https://uberspace.de/en/'>Uberspace</a>"
DONATE = "<a href='https://www.buymeacoffee.com/searchatfuture'>DONATE</a>"
COLABORATE = "<a href='https://github.com/rtrevinnoc/FUTURE'>COLABORATE</a>"
```

**NOTE:** In case you want to use a docker container, simpy run the following commands before everything else below (Or use the pre-built image from [DockerHub](https://hub.docker.com/repository/docker/rtrevinnoc/future)):

```bash
docker build -t future .
docker run -i -t -p 3000:3000 future bash
```

After you have configurated your FUTURE instance, but before you can start the server, you will be required to add a minimum of ~25 urls to your local index, by executing:

```bash
chmod +x bootstrap.sh
./bootstrap.sh
./build_index.sh
```

At any point in time, you can check how much webpages are in your local index by executing:

```bash
python3 count_index.py
```

And eventually, you can interrupt the crawler by executing:

```bash
./save_index.sh
```

Naturally, you can restart it using `./build_index.sh`. And with this, you can start your development server with:

```bash
./future.py
```

However, if you are planning to contribute to the shared index by making your instance public, it is recommended to use uWSGI. We suggest using this configuration template, with `touch uwsgi.ini`, as it is used on the main instance.

```yaml
[uwsgi]
module = future:app
pidfile = future.pid
http-socket = :3000
chmod-socket = 660
strict = true
master = true
enable-threads = true
vacuum = true                        ; Delete sockets during shutdown
single-interpreter = true
die-on-term = true                   ; Shutdown when receiving SIGTERM (default is respawn)
need-app = true

disable-logging = true               ; Disable built-in logging
log-4xx = true                       ; but log 4xx's anyway
log-5xx = true                       ; and 5xx's

cheaper-algo = busyness
processes = 6                        ; Maximum number of workers allowed
cheaper = 1                          ; Minimum number of workers allowed
cheaper-initial = 2                  ; Workers created at startup
cheaper-overload = 1                 ; Length of a cycle in seconds
cheaper-step = 1                     ; How many workers to spawn at a time

cheaper-busyness-multiplier = 30     ; How many cycles to wait before killing workers
cheaper-busyness-min = 20            ; Below this threshold, kill workers (if stable for multiplier cycles)
cheaper-busyness-max = 70            ; Above this threshold, spawn new workers
cheaper-busyness-backlog-alert = 4   ; Spawn emergency workers if more than this many requests are waiting in the queue
cheaper-busyness-backlog-step = 2    ; How many emergency workers to create if there are too many requests in the queue
```

Finally, start your public node to contribute to the shared network with the following command:

```bash
uwsgi uwsgi.ini
```


## DEPENDENCIES

Below are listed all the projects upon which __FUTURE__ rests.
Name | License
---|---
[Flask](https://github.com/pallets/flask)|BSD 3-Clause
[Werkzeug](https://github.com/pallets/werkzeug)|BSD 3-Clause                
[SymSpell](https://github.com/wolfgarbe/SymSpell/)|MIT
[Polyglot](https://github.com/aboSamoor/polyglot/)|GPL v3                   
[Beautifulsoup ](https://code.launchpad.net/beautifulsoup)|BSD 2-Clause              
[BSON Python bindings](https://github.com/py-bson/bson)|Apache 2.0                
[NumPy](https://github.com/numpy/numpy)|BSD 3-Clause     
[GeoPy](https://github.com/geopy/geopy)|MIT                   
[SciKit Learn](https://github.com/scikit-learn/scikit-learn)|BSD 3-Clause                 
[Pandas](https://github.com/pandas-dev/pandas)|BSD 3-Clause     
[Gensim](https://github.com/RaRe-Technologies/gensim)|LGPL 2.1                      
[NLTK](https://github.com/nltk/nltk)|Apache 2.0      
[Scrapy](https://github.com/scrapy/scrapy)|BSD License                   
[H5PY](https://github.com/h5py/h5py)|BSD 3-Clause              
[LMBD](https://github.com/LMDB/lmdb)|OpenLDAP
[LMBD Python bindings](https://github.com/jnwatson/py-lmdb)|OpenLDAP                    
[tldextract](https://github.com/john-kurkowski/tldextract)|BSD 3-Clause       
[WTForms](https://github.com/wtforms/wtforms)|BSD 3-Clause               
[Flask_wtf](https://github.com/lepture/flask-wtf)|BSD 3-Clause
[HNSWLib](https://github.com/nmslib/hnswlib)|Apache 2.0
[JQuery](https://github.com/jquery/jquery)|MIT                      
[JQuery UI](https://github.com/jquery/jquery-ui)|MIT             
[Particles JS](https://github.com/VincentGarreau/particles.js/)|MIT             
[Ionicons](https://github.com/ionic-team/ionicons)|MIT         
[Source Sans Pro](https://github.com/adobe-fonts/source-sans-pro)|OFL 1.1                   
[GloVe](https://github.com/stanfordnlp/GloVe)|Apache 2.0
[SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper)|W3C License      
[TextScrambler](https://codepen.io/soulwire/pen/mErPAK)|BSD-like   



### FUTURE on w3m

[![asciicast](https://asciinema.org/a/331246.svg)](https://asciinema.org/a/331246?autoplay=1)
