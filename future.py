#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Copyright (c) 2020 Roberto Treviño Cervantes

#########################################################################
#                                                                       #
# This file is part of FUTURE (Powered by Monad).                       #
#                                                                       #
# FUTURE is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# FUTURE is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with FUTURE.  If not, see <https://www.gnu.org/licenses/>.      #
#                                                                       #
#########################################################################

from Monad import *
import os.path, os, shutil, json, random, sys, socket, re, mimetypes, datetime, lmdb, hnswlib, time, bson, requests, socket, ast, functools, asyncio, concurrent.futures, itertools
import numpy as np
from flask import (Flask, render_template, request, redirect,
                   send_from_directory, flash, abort, jsonify, escape,
                   Response)
from forms import *
# from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename
from base64 import b64decode
from symspellpy.symspellpy import SymSpell, Verbosity
from bs4 import BeautifulSoup
from config import HOST_NAME, PEER_PORT

bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode

global port, hostIP, hostname, listOfPeers, app, hnswImagesLookup, imageDBIndex, analyticsDBIndex, spellChecker, dirname, numberOfURLs, goodSearxInstances, headersForSearx
port = int(PEER_PORT)
hostIP = requests.get(
    "https://api.ipify.org?format=json").json()["ip"] + ":" + str(port)
hostname = HOST_NAME
listOfPeers = []
numberOfURLs = 5  # LATER ADD SUPORT TO ONLY GET IMPORTANT URLS
dirname = os.path.dirname(__file__)
app = Flask(__name__, static_url_path="")
app.config.from_pyfile(os.path.abspath("config.py"))
np.random.seed(0)
hnswImagesLookup = hnswlib.Index(space="cosine", dim=50)
hnswImagesLookup.load_index("FUTURE_images_vecs.bin", max_elements=100000)
hnswImagesLookup.set_ef(100)
imageDBIndex = lmdb.open("future_images", map_size=int(1e12), writemap=True)
peerRegistry = lmdb.open("peer_registry", map_size=int(1e12), writemap=True)
peerRegistryTransaction = peerRegistry.begin(write=True)
peerRegistryTransaction.put("wearebuildingthefuture.com".encode('utf-8'),
                            "".encode('utf-8'),
                            overwrite=False)
peerRegistryTransaction.put(hostIP.encode('utf-8'),
                            "".encode('utf-8'),
                            overwrite=False)
peerRegistryTransaction.commit()
analyticsDBIndex = lmdb.open("future_analytics",
                             map_size=int(1e12),
                             writemap=True)
FUTURE = Monad("future_urls")
FUTURE.loadIndex("FUTURE_url_vecs")
spellChecker = SymSpell(
    2,
    7)  # PARAMETERS INDICATE (MAX EDIT DISTANCE DICTIONARY AND PREFIX LENGTH)
spellChecker.load_dictionary(
    "./frequency_dictionary_en_82_765.txt", 0, 1
)  # LAST TWO PARAMETERS ARE (COLUMN TERM, FREQUENCY TERM) LOCATIONS IN DICTIONARY FILE


def sendRegisterRequestToPeer(url):
    peer = url.decode("utf-8")
    print("#######################")
    print("host:, ", hostIP)
    print("peer:, ", peer)
    print("#######################")
    if peer == hostIP or peer == hostname:
        print("Same as origin")
        return "Same as origin"
    else:
        try:
            r = requests.get("http://" + peer + "/_registerPeer",
                             params={'ip': hostIP},
                             timeout=10)
            peerRegistryTransaction = peerRegistry.begin(write=True)
            for newPeer in r.json()["result"]["listOfPeers"]:
                peerRegistryTransaction.put(newPeer.encode('utf-8'),
                                            "".encode('utf-8'),
                                            overwrite=False)
            peerRegistryTransaction.commit()
            print("Registered with http")
            return "Registered with http"
        except:
            try:
                r = requests.get("https://" + peer + "/_registerPeer",
                                 params={'ip': hostIP},
                                 timeout=10)
                peerRegistryTransaction = peerRegistry.begin(write=True)
                for newPeer in r.json()["result"]["listOfPeers"]:
                    peerRegistryTransaction.put(newPeer.encode('utf-8'),
                                                "".encode('utf-8'),
                                                overwrite=False)
                peerRegistryTransaction.commit()
                print("Registered with https")
                return "Registered with https"
            except:
                print("Could not connect with peer")
                return "Could not connect with peer"


def sendAnswerRequestToPeer(url, query, queryVector, queryLanguage,
                            numberOfURLs, numberOfPage):
    peer = url
    queryVector = json.dumps(queryVector.tolist())
    print("#######################")
    print("host:, ", hostIP)
    print("peer:, ", peer)
    print("#######################")
    if peer == hostIP or peer == hostname:
        print("Same as origin")
        return {"urls": [], "images": []}
    else:
        try:
            r = requests.get("http://" + peer + "/_answerPeer",
                             params={
                                 'query': query,
                                 'q_vec': queryVector,
                                 'queryLanguage': queryLanguage,
                                 'numberOfURLs': numberOfURLs,
                                 'numberOfPage': numberOfPage
                             },
                             timeout=10)
            result = r.json()["result"]
            print("Obtained with http")
            return {
                "urls": list(zip(result["urls"], result["url_scores"])),
                "images": list(zip(result["images"], result["images_scores"]))
            }
        except:
            try:
                r = requests.get("https://" + peer + "/_answerPeer",
                                 params={
                                     'query': query,
                                     'q_vec': queryVector,
                                     'queryLanguage': queryLanguage,
                                     'numberOfURLs': numberOfURLs,
                                     'numberOfPage': numberOfPage
                                 },
                                 timeout=10)
                result = r.json()["result"]
                print("Obtained with https")
                return {
                    "urls": list(zip(result["urls"], result["url_scores"])),
                    "images":
                    list(zip(result["images"], result["images_scores"]))
                }
            except:
                print("Could not connect with peer")
                return {"urls": [], "images": []}


with peerRegistry.begin() as peerRegistryDBTransaction:
    peerRegistryDBSelector = peerRegistryDBTransaction.cursor()
    for key, value in peerRegistryDBSelector:
        listOfPeers.append(key.decode("utf-8"))
        sendRegisterRequestToPeer(key)


searxInstances = requests.get("https://searx.space/data/instances.json").json()["instances"]
goodSearxInstances = filter(lambda x: x[1].get("timing").get("search").get("error") == None, filter(lambda x: x[1].get("timing").get("search")["success_percentage"] >= 90, filter(lambda x: x[1].get("timing").get("search") != None, filter(lambda x: type(x[1].get("timing")) == dict, searxInstances.items()))))
goodSearxInstances = filter(lambda x: x[1].get("tls")["grade"] == "A+", filter(lambda x: x[1].get("tls") != None, filter(lambda x: x[1]["network_type"] == "normal", goodSearxInstances)))
goodSearxInstances = sorted(goodSearxInstances, key=lambda x: x[1]["timing"]["search"]["all"]["mean"])


headersForSearx = {
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "en-US,en;q=0.5", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0", 
    "X-Amzn-Trace-Id": "Root=1-5ff4f39d-43753d3a161269974fdca42e"
}


async def getDataFromPeers(query, queryVector, queryLanguage, numberOfURLs,
                           numberOfPage):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                functools.partial(sendAnswerRequestToPeer, peer, query,
                                  queryVector, queryLanguage, numberOfURLs,
                                  numberOfPage)) for peer in listOfPeers
        ]
        listOfResponses = []
        for response in await asyncio.gather(*futures):
            listOfResponses.append(response)
        return listOfResponses


def loadMoreUrls(q_vec: np.ndarray, queryLanguage: str, numberOfURLs: int,
                 page: int):
    search = FUTURE.searchIndex(q_vec, numberOfURLs, page)

    urls = [{
        "url": escapeHTMLString(url["url"]),
        "header": escapeHTMLString(url["header"]),
        "body": escapeHTMLString(url["body"]),
        "language": url["language"],
    } for url in search["results"]]

    urlsInPreferedLanguage, urlsInOtherLanguages = [], []
    for url in urls:
        if url["language"] == queryLanguage:
            urlsInPreferedLanguage.append(url)
        else:
            urlsInOtherLanguages.append(url)
    urls = urlsInPreferedLanguage + urlsInOtherLanguages

    return {"urls": urls, "scores": search["vectorScores"]}


def loadMoreImages(term: np.ndarray, number, page: int) -> dict:
    with imageDBIndex.begin() as imageDBTransaction:
        databaseLimit = imageDBTransaction.stat()["entries"]
        totalItems = number * page
        if totalItems <= databaseLimit:
            vectorIds, vectorScores = hnswImagesLookup.knn_query(term,
                                                                 k=totalItems)
        else:
            raise ValueError(
                "Number of items to fetch higher than items in database.")

        if page > 1:
            lowerLimit = number * (page - 1)
        elif page == 1:
            lowerLimit = 0

        resultImages = []
        for image in vectorIds[0][lowerLimit:totalItems]:
            image = bson.loads(imageDBTransaction.get(str(image).encode("utf-8")))
            resultImages.append({"url": image["url"], "parentUrl": image["parentUrl"]})

        return {
            "images": resultImages,
            "vectorIds":
            vectorIds[0][lowerLimit:totalItems],
            "scores":
            vectorScores[0][lowerLimit:totalItems]
        }


def answer(query: str) -> jsonify:
    start = time.time()
    queryBeforePreprocessing = query
    queryLanguage = inferLanguage(query)
    if getResourceFromDBPedia(
            queryBeforePreprocessing)["verification"] == False:
        spellCheckerSuggestions = spellChecker.lookup_compound(
            query, 2)  # LAST PARAMETER INDICATES MAX EDIT DISTANCE LOOKUP
        query = " ".join(
            [suggestion.term for suggestion in spellCheckerSuggestions])
    else:
        query = queryBeforePreprocessing
    query = query.lower()
    try:
        q_vec = getSentenceMeanVector(query)
    except:
        return {
            "answer": "No relevant information available.",
            "small_summary": "No relevant information available.",
            "time": time.time() - start,
            "corrected": query,
            "urls": [],
            "images": [],
            "n_res": 0,
            "map": "",
        }

    if len(query) <= 160:
        with analyticsDBIndex.begin(write=True) as analyticsDBTransaction:
            queryBytes = query.encode("utf-8")
            analyticsPreviousValue = analyticsDBTransaction.get(queryBytes)
            if analyticsPreviousValue == None:
                analyticsDBTransaction.put(queryBytes, str(0).encode("utf-8"))
            else:
                analyticsDBTransaction.put(
                    queryBytes,
                    str(int(analyticsPreviousValue.decode("utf-8")) +
                        1).encode("utf-8"))
    # imageVectorIds, imageVectorScores = hnswImagesLookup.knn_query(q_vec, k=50)
    images = loadMoreImages(q_vec, 50, 1)
    urls = loadMoreUrls(q_vec, queryLanguage, numberOfURLs, 1)

    # with imageDBIndex.begin() as imageDBTransaction:
    # imagesBinaryDictionary = [
    # bson.loads(imageDBTransaction.get(
    # str(image).encode("utf-8")))["url"]
    # for image in imageVectorIds[0]
    # ]  # [:n_imgs]]

    listOfDataFromPeers = asyncio.run(
        getDataFromPeers(query, q_vec, queryLanguage, numberOfURLs, 1))
    if len(listOfDataFromPeers) > 0:
        listOfUrlsFromHost = list(zip(urls["urls"], urls["scores"]))
        listOfImagesFromHost = list(zip(images["images"], images["scores"]))
        listOfUrlsFromPeers = list(
            itertools.chain(*[pack["urls"] for pack in listOfDataFromPeers]))
        listOfImagesFromPeers = list(
            itertools.chain(*[pack["images"] for pack in listOfDataFromPeers]))
        bigListOfUrls = listOfUrlsFromHost + listOfUrlsFromPeers
        # bigListOfImages = list(
            # set(listOfImagesFromHost + listOfImagesFromPeers))
        bigListOfImages = listOfImagesFromHost + listOfImagesFromPeers
        bigListOfUrls.sort(key=lambda x: x[1])
        bigListOfImages.sort(key=lambda x: x[1])
        bigListOfUrls = [url[0] for url in bigListOfUrls]
        bigListOfImages = [
            image[0] for image in bigListOfImages if image[0] != ''
        ]
    else:
        bigListOfUrls = urls["urls"]
        bigListOfImages = images["images"]

    try:
        DBPediaDef = getDefinitionFromDBPedia(query)
    except:
        DBPediaDef = "Brief description not found."

    return {
        "answer":
        escapeHTMLString(getAbstractFromDBPedia(query)),
        "small_summary":
        escapeHTMLString(DBPediaDef),
        "time":
        time.time() - start,
        "corrected":
        escapeHTMLString(query),
        "urls":
        list({frozenset(item.items()): item
              for item in bigListOfUrls}.values()),
        "images":
        list({frozenset(item.items()): item
              for item in bigListOfImages}.values()),
        "n_res":
        len(bigListOfUrls),
        "map":
        getMap(queryBeforePreprocessing, query),
    }


def answerPeer(query: str, q_vec: list, queryLanguage: str, numberOfURLs: int,
               numberOfPage: int) -> jsonify:
    q_vec = np.array(ast.literal_eval("".join(q_vec)))
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(q_vec)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    if len(query) <= 160:
        with analyticsDBIndex.begin(write=True) as analyticsDBTransaction:
            queryBytes = query.encode("utf-8")
            analyticsPreviousValue = analyticsDBTransaction.get(queryBytes)
            if analyticsPreviousValue == None:
                analyticsDBTransaction.put(queryBytes, str(0).encode("utf-8"))
            else:
                analyticsDBTransaction.put(
                    queryBytes,
                    str(int(analyticsPreviousValue.decode("utf-8")) +
                        1).encode("utf-8"))

    # imageVectorIds, imageVectorScores = hnswImagesLookup.knn_query(q_vec, k=50)
    images = loadMoreImages(q_vec, 50, numberOfPage)
    urls = loadMoreUrls(q_vec, queryLanguage, numberOfURLs, numberOfPage)

    # with imageDBIndex.begin() as imageDBTransaction:
    # imagesBinaryDictionary = [
    # bson.loads(imageDBTransaction.get(
    # str(image).encode("utf-8")))["url"]
    # for image in imageVectorIds[0]
    # ]  # [:n_imgs]]

    return {
        "urls": urls["urls"],
        "url_scores": urls["scores"].tolist(),
        "images": images["images"],
        "images_scores": images["scores"].tolist()
    }


@app.route('/_registerPeer')
def _registerPeer():
    peerIP = request.args.get("ip", 0, type=str)
    print("gotten")
    peerRegistryTransaction = peerRegistry.begin(write=True)
    peerRegistryTransaction.put(str(peerIP).encode('utf-8'),
                                "".encode('utf-8'),
                                overwrite=False)
    peerRegistryTransaction.commit()

    return jsonify(result={"listOfPeers": listOfPeers})


@app.route('/_fetchSearxResults', methods=['GET'])
def fetchSearxResults():
    query = request.args.get("query", 0, type=str)

    queryBeforePreprocessing = query
    if getResourceFromDBPedia(
            queryBeforePreprocessing)["verification"] == False:
        spellCheckerSuggestions = spellChecker.lookup_compound(
            query, 2)  # LAST PARAMETER INDICATES MAX EDIT DISTANCE LOOKUP
        query = " ".join(
            [suggestion.term for suggestion in spellCheckerSuggestions])
    else:
        query = queryBeforePreprocessing

    while True:
        try:
            resultURLsFromSearx = requests.get(goodSearxInstances[int(random.random() * len(goodSearxInstances))][0] + "search", headers=headersForSearx, params={'q': query, 'format': 'json'}, timeout=5).json()['results']
            resultURLsFromSearx = [{'url': result.get('url', "No URL available."), 'header': result.get('title', "No header available."), 'body': result.get('content', "No description available.")} for result in resultURLsFromSearx]
            break
        except:
            pass

    while True:
        try:
            resultImagesFromSearx = requests.get(goodSearxInstances[int(random.random() * len(goodSearxInstances))][0] + "search", headers=headersForSearx, params={'q': query, 'format': 'json', 'categories': 'images'}, timeout=5).json()['results']
            resultImagesFromSearx = [{'url': result.get('img_src', ""), 'parentUrl': result.get('url', "")} for result in resultImagesFromSearx]
            break
        except:
            pass

    return jsonify(
        result={
            "urls":
            list({frozenset(item.items()): item
                  for item in resultURLsFromSearx}.values()),
            "images":
            list({frozenset(item.items()): item
                  for item in resultImagesFromSearx}.values())
        })


@app.route('/sw.js', methods=['GET'])
def sw():
    return send_from_directory(".", "sw.js")


@app.route("/particles_white.json")
def particlesWhite():
    return send_from_directory("static/js/", "particles_white.json")


@app.route("/particles_black.json")
def particlesBlack():
    return send_from_directory("static/js/", "particles_black.json")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        currentPage = request.form.get("current_page", 0, type=int)
        if currentPage:
            nextPage = request.form.get("next_page", 0, type=bool)
            lastPage = request.form.get("last_page", 0, type=bool)
            previousQuery = request.form.get("previous_query", 0, type=str)
            q_vec = getSentenceMeanVector(previousQuery)
            queryLanguage = inferLanguage(previousQuery)
            if nextPage:
                followingPage = currentPage + 1
            elif lastPage:
                if currentPage == 1:
                    followingPage = 1
                else:
                    followingPage = currentPage - 1
            return render_template("answer.html",
                                   previousQuery=previousQuery,
                                   section="links",
                                   answer=loadMoreUrls(q_vec, queryLanguage,
                                                       numberOfURLs,
                                                       followingPage)["urls"],
                                   currentPage=followingPage)

        query = request.form.get("a", 0, type=str)
        response = answer(query)

        if request.form.get("links", 0, type=bool):
            return render_template("answer.html",
                                   previousQuery=query,
                                   section="links",
                                   answer=response["urls"],
                                   currentPage=1)
        elif request.form.get("summary", 0, type=bool):
            return render_template("answer.html",
                                   previousQuery=query,
                                   section="summary",
                                   answer=response["answer"],
                                   currentPage=1)
        elif request.form.get("images", 0, type=bool):
            return render_template("answer.html",
                                   previousQuery=query,
                                   section="images",
                                   answer=response["images"],
                                   currentPage=1)
        elif request.form.get("maps", 0, type=bool):
            return render_template("answer.html",
                                   previousQuery=query,
                                   section="maps",
                                   answer=response["map"],
                                   currentPage=1)
        else:
            return render_template("answer.html",
                                   previousQuery=query,
                                   section="summary",
                                   answer=response["answer"],
                                   currentPage=1)
    return render_template("index.html", name=None)


@app.route("/_autocomplete", methods=["GET", "POST"])
def _autocomplete():
    term = request.args.get("term", 0, type=str)
    type_arg = request.args.get("type", "list", type=str)
    with analyticsDBIndex.begin() as analyticsDBTransaction:
        analyticsDBSelector = analyticsDBTransaction.cursor()
        decodedPreviousQueries = [(str(key.decode("utf-8")), int(value))
                                  for key, value in analyticsDBSelector]
        similarPreviousQueries = [
            innerlist[0] for innerlist in sorted([
                query for query in decodedPreviousQueries
                if query[0].startswith(term)
            ][:5],
                                                 key=lambda x: x[1],
                                                 reverse=True)
        ] 
        if type_arg == "list":
            return Response(json.dumps([term, similarPreviousQueries]),
                    mimetype='application/json')
        else:
            return Response(json.dumps(similarPreviousQueries),
                    mimetype='application/json')


@app.route("/_answer")
def _answer():
    """The method for processing form data and answering."""
    query = request.args.get("query", 0, type=str)
    return jsonify(result=answer(query))


@app.route("/_answerPeer")
def _answerPeer():
    """The method for processing form data and answering."""
    query = request.args.get("query", 0, type=str)
    q_vec = request.args.get("q_vec", 0, type=str)
    queryLanguage = request.args.get("queryLanguage", 0, type=str)
    numberOfURLs = request.args.get("numberOfURLs", 0, type=int)
    numberOfPage = request.args.get("numberOfPage", 1, type=int)
    return jsonify(result=answerPeer(query, q_vec, queryLanguage, numberOfURLs,
                                     numberOfPage))


@app.route("/_updateAnswer", methods=["GET", "POST"])
def _updateAnswer():
    query = request.args.get("query", 0, type=str)
    page = request.args.get("page", 0, type=int)
    q_vec = getSentenceMeanVector(query)
    queryLanguage = inferLanguage(query)

    urls = loadMoreUrls(q_vec, queryLanguage, numberOfURLs, page)
    images = loadMoreImages(q_vec, 50, page)

    listOfDataFromPeers = asyncio.run(
        getDataFromPeers(query, q_vec, queryLanguage, numberOfURLs, page))
    if len(listOfDataFromPeers) > 0:
        listOfUrlsFromHost = list(zip(urls["urls"], urls["scores"]))
        listOfImagesFromHost = list(zip(images["images"], images["scores"]))
        listOfUrlsFromPeers = [pack["urls"] for pack in listOfDataFromPeers][0]
        listOfImagesFromPeers = [
            pack["images"] for pack in listOfDataFromPeers
        ][0]
        bigListOfUrls = listOfUrlsFromHost + listOfUrlsFromPeers
        bigListOfImages = list(
            set(listOfImagesFromHost + listOfImagesFromPeers))
        bigListOfUrls.sort(key=lambda x: x[1])
        bigListOfImages.sort(key=lambda x: x[1])
        bigListOfUrls = [url[0] for url in bigListOfUrls]
        bigListOfImages = [
            image[0] for image in bigListOfImages if image[0] != ''
        ]
    else:
        bigListOfUrls = urls["urls"]
        bigListOfImages = images["images"]

    return jsonify(
        result={
            "urls":
            list({frozenset(item.items()): item
                  for item in bigListOfUrls}.values()),
            "images":
            bigListOfImages
        })


@app.route("/_midnightcypher")
def _midnightcypher():
    query = request.args.get("query", 0, type=str)
    q_vec = getSentenceMeanVector(query)
    imageVectorIds, _ = hnswImagesLookup.knn_query(q_vec, k=50)

    with imageDBIndex.begin() as imageDBTransaction:
        imagesBinaryDictionary = [
            bson.loads(imageDBTransaction.get(
                str(image).encode("utf-8")))["url"]
            for image in imageVectorIds[0]
        ]  # [:n_imgs]]

    return jsonify(result={
        "images": imagesBinaryDictionary,
    })


if __name__ == "__main__":
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host="0.0.0.0", port=port, debug=True)
