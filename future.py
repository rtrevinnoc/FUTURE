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
import os.path, os, shutil, json, random, sys, socket, re, mimetypes, datetime, lmdb, hnswlib, time, bson, requests, socket, ast, functools, asyncio, concurrent.futures, itertools, mimetypes, io, threading, languagecodes, psutil
import numpy as np
import numexpr as ne
from flask import (Flask, render_template, request, redirect,
                   send_from_directory, flash, abort, jsonify, escape,
                   Response, send_file)
from werkzeug.middleware.proxy_fix import ProxyFix
# from werkzeug.contrib.fixers import ProxyFix
from flask_caching import Cache
from werkzeug.utils import secure_filename
from base64 import b64decode
from symspellpy.symspellpy import SymSpell, Verbosity
from bs4 import BeautifulSoup
from config import HOST_NAME, PEER_PORT, HOME_URL, CACHE_TIMEOUT, CACHE_THRESHOLD
from PIL import Image

bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode

global port, hostIP, hostname, listOfPeers, numberOfPeers, app, hnswImagesLookup, imageDBIndex, analyticsDBIndex, spellChecker, dirname, numberOfURLs, cache
port = int(PEER_PORT)
hostIP = requests.get(
    "https://api.ipify.org?format=json").json()["ip"] + ":" + str(port)
hostname = HOST_NAME
listOfPeers = []
numberOfPeers = 0
numberOfURLs = 5  # LATER ADD SUPORT TO ONLY GET IMPORTANT URLS
dirname = os.path.dirname(__file__)
app = Flask(__name__, static_url_path="")
app.config.from_pyfile(os.path.abspath("config.py"))
np.random.seed(0)
hnswImagesLookup = hnswlib.Index(space="cosine", dim=50)
hnswImagesLookup.load_index("FUTURE_images_vecs.bin", max_elements=1000000)
hnswImagesLookup.set_ef(100)
imageDBIndex = lmdb.open("future_images", map_size=int(1e12), writemap=True)
peerRegistry = lmdb.open("peer_registry", map_size=int(1e12), writemap=True)
peerRegistryTransaction = peerRegistry.begin(write=True)
peerRegistryTransaction.put(HOME_URL.encode('utf-8'),
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
cache = Cache(app,
              config={
                  'CACHE_TYPE': 'filesystem',
                  'CACHE_DEFAULT_TIMEOUT': CACHE_TIMEOUT,
                  'CACHE_THRESHOLD': CACHE_THRESHOLD,
                  'CACHE_DIR': './external_image_cache'
              })


def sendRegisterRequestToPeer(url):
    global listOfPeers, numberOfPeers
    peer = url.decode("utf-8")
    print("#######################")
    print("host:, ", hostIP)
    print("peer:, ", peer)
    print("#######################")
    if peer == hostIP or peer == hostname:
        if hostname == HOME_URL:
            listOfPeers.append(hostname)
        elif peer != hostname:
            listOfPeers.append(peer)
        listOfPeers = list(set(listOfPeers))
        numberOfPeers += 1
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
            listOfPeers.append(peer)
            listOfPeers = list(set(listOfPeers))
            numberOfPeers += 1
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
                listOfPeers.append(peer)
                listOfPeers = list(set(listOfPeers))
                numberOfPeers += 1
                print("Registered with https")
                return "Registered with https"
            except:
                print("Could not connect with peer")
                return "Could not connect with peer"


def sendAnswerRequestToPeer(url, query, queryVector, queryLanguage,
                            numberOfURLs, numberOfPage, minimumScore):
    global listOfPeers, numberOfPeers
    peer = url
    queryVector = json.dumps(queryVector.tolist())
    print("#######################")
    print("host:, ", hostIP)
    print("peer:, ", peer)
    print("#######################")
    if peer == hostIP or peer == hostname:
        print("Same as origin")
        return {"urls": []}
    else:
        try:
            r = requests.get("http://" + peer + "/_answerPeer",
                             params={
                                 'query': query,
                                 'q_vec': queryVector,
                                 'queryLanguage': queryLanguage,
                                 'numberOfURLs': numberOfURLs,
                                 'numberOfPage': numberOfPage,
                                 'minimumScore': minimumScore
                             },
                             timeout=10)
            result = r.json()["result"]
            listOfPeers.append(peer)
            listOfPeers = list(set(listOfPeers))
            numberOfPeers += 1
            print("Obtained with http")
            return {"urls": list(zip(result["urls"], result["url_scores"]))}
        except:
            try:
                r = requests.get("https://" + peer + "/_answerPeer",
                                 params={
                                     'query': query,
                                     'q_vec': queryVector,
                                     'queryLanguage': queryLanguage,
                                     'numberOfURLs': numberOfURLs,
                                     'numberOfPage': numberOfPage,
                                     'minimumScore': minimumScore
                                 },
                                 timeout=10)
                result = r.json()["result"]
                listOfPeers.append(peer)
                listOfPeers = list(set(listOfPeers))
                numberOfPeers += 1
                print("Obtained with https")
                return {
                    "urls": list(zip(result["urls"], result["url_scores"]))
                }
            except:
                try:
                    listOfPeers.remove(peer)
                    numberOfPeers -= 1
                except:
                    pass
                print("Could not connect with peer")
                return {"urls": []}


def sendImagesAnswerRequestToPeer(url, query, queryVector, queryLanguage,
                                  numberOfURLs, numberOfPage, minimumScore):
    global listOfPeers, numberOfPeers
    peer = url
    queryVector = json.dumps(queryVector.tolist())
    print("#######################")
    print("host:, ", hostIP)
    print("peer:, ", peer)
    print("#######################")
    if peer == hostIP or peer == hostname:
        print("Same as origin")
        return {"images": []}
    else:
        try:
            r = requests.get("http://" + peer + "/_answerPeerImages",
                             params={
                                 'query': query,
                                 'q_vec': queryVector,
                                 'queryLanguage': queryLanguage,
                                 'numberOfURLs': numberOfURLs,
                                 'numberOfPage': numberOfPage,
                                 'minimumScore': minimumScore
                             },
                             timeout=10)
            result = r.json()["result"]
            listOfPeers.append(peer)
            listOfPeers = list(set(listOfPeers))
            numberOfPeers += 1
            print("Obtained with http")
            return {
                "images": list(zip(result["images"], result["images_scores"]))
            }
        except:
            try:
                r = requests.get("https://" + peer + "/_answerPeerImages",
                                 params={
                                     'query': query,
                                     'q_vec': queryVector,
                                     'queryLanguage': queryLanguage,
                                     'numberOfURLs': numberOfURLs,
                                     'numberOfPage': numberOfPage,
                                     'minimumScore': minimumScore
                                 },
                                 timeout=10)
                result = r.json()["result"]
                listOfPeers.append(peer)
                listOfPeers = list(set(listOfPeers))
                numberOfPeers += 1
                print("Obtained with https")
                return {
                    "images":
                    list(zip(result["images"], result["images_scores"]))
                }
            except:
                try:
                    listOfPeers.remove(peer)
                    numberOfPeers -= 1
                except:
                    pass
                print("Could not connect with peer")
                return {"images": []}


if hostname != "private":
    with peerRegistry.begin() as peerRegistryDBTransaction:
        peerRegistryDBSelector = peerRegistryDBTransaction.cursor()
        for key, value in peerRegistryDBSelector:
            sendRegisterRequestToPeer(key)
    numberOfPeers = len(listOfPeers)


async def getDataFromPeers(query, queryVector, queryLanguage, numberOfURLs,
                           numberOfPage, minimumScore):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                functools.partial(sendAnswerRequestToPeer, peer, query,
                                  queryVector, queryLanguage, numberOfURLs,
                                  numberOfPage, minimumScore))
            for peer in listOfPeers
        ]
        listOfResponses = []
        for response in await asyncio.gather(*futures):
            listOfResponses.append(response)
            if numberOfPeers >= 5 and len(listOfResponses) == 5:
                return listOfResponses
            else:
                continue
        return listOfResponses


async def getImagesFromPeers(query, queryVector, queryLanguage, numberOfURLs,
                             numberOfPage, minimumScore):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                functools.partial(sendImagesAnswerRequestToPeer, peer, query,
                                  queryVector, queryLanguage, numberOfURLs,
                                  numberOfPage, minimumScore))
            for peer in listOfPeers
        ]
        listOfResponses = []
        for response in await asyncio.gather(*futures):
            listOfResponses.append(response)
            if numberOfPeers >= 5 and len(listOfResponses) == 5:
                return listOfResponses
            else:
                continue
        return listOfResponses


def loadMoreUrls(q_vec: np.ndarray, queryLanguage: str, numberOfURLs: int,
                 page: int):
    try:
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
    except:
        return {"urls": [], "scores": []}


def loadMoreImages(term: np.ndarray, number, page: int) -> dict:
    try:
        with imageDBIndex.begin() as imageDBTransaction:
            databaseLimit = imageDBTransaction.stat()["entries"]
            totalItems = number * page
            if totalItems <= databaseLimit:
                vectorIds, vectorScores = hnswImagesLookup.knn_query(
                    term, k=totalItems)
            else:
                raise ValueError(
                    "Number of items to fetch higher than items in database.")

            if page > 1:
                lowerLimit = number * (page - 1)
            elif page == 1:
                lowerLimit = 0

            resultImages = []
            for idx, image in enumerate(vectorIds[0][lowerLimit:totalItems]):
                image = bson.loads(
                    imageDBTransaction.get(str(image).encode("utf-8")))

                resultImages.append({
                    "url": image["url"],
                    "parentUrl": image["parentUrl"]
                })

            return {
                "images": resultImages,
                "vectorIds": vectorIds[0][lowerLimit:totalItems],
                "scores": vectorScores[0][lowerLimit:totalItems]
            }
    except:
        return {"images": [], "vectorIds": [], "scores": []}


def registerQueryInAnalytics(query: str):
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


def answer(query: str, page: int) -> jsonify:
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
    query = query.lower().strip()
    if queryLanguage != "en":
        try:
            query = requests.get(
                "https://www.apertium.org/apy/translate",
                params={
                    'q':
                    query,
                    'markUnknown':
                    'no',
                    'langpair':
                    languagecodes.iso_639_alpha3(queryLanguage) + '|eng'
                }).json()['responseData']['translatedText']
        except:
            pass
            # return {
                # "answer": "Could not translate input.",
                # "small_summary": "Could not translate input.",
                # "corrected": query,
                # "urls": []
            # }
    try:
        q_vec = getSentenceMeanVector(query)
    except:
        return {
            "answer": "No relevant information available.",
            "small_summary": "No relevant information available.",
            "corrected": query,
            "urls": []
        }

    urls = loadMoreUrls(q_vec, queryLanguage, numberOfURLs, page)
    try:
        minimumScore = max(urls["scores"])
    except:
        minimumScore = 1

    listOfDataFromPeers = asyncio.run(
        getDataFromPeers(query, q_vec, queryLanguage, numberOfURLs, page,
                         minimumScore))
    if len(listOfDataFromPeers) > 0:
        listOfUrlsFromHost = list(zip(urls["urls"], urls["scores"]))
        listOfUrlsFromPeers = list(
            itertools.chain(*[pack["urls"] for pack in listOfDataFromPeers]))
        bigListOfUrls = listOfUrlsFromHost + listOfUrlsFromPeers
        bigListOfUrls.sort(key=lambda x: x[1])
        bigListOfUrls = [url[0] for url in bigListOfUrls]
    else:
        bigListOfUrls = urls["urls"]

    try:
        DBPediaDef = getDefinitionFromDBPedia(query)
    except:
        try:
            DBPediaDef = query + " = " + str(ne.evaluate(query)[()])
        except:
            DBPediaDef = "Brief description not found."

    bigListOfUrls = list(
        {frozenset(item.items()): item
         for item in bigListOfUrls}.values())

    if page == 1:
        registerQueryInAnalytics(query)
        return {
            "answer": escapeHTMLString(getAbstractFromDBPedia(query)),
            "small_summary": escapeHTMLString(DBPediaDef),
            "corrected": escapeHTMLString(query),
            "urls": bigListOfUrls[:15]
        }
    else:
        return {"urls": bigListOfUrls[:15]}


def answerImages(query: str, page: int) -> jsonify:
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
    query = query.lower().strip()
    try:
        q_vec = getSentenceMeanVector(query)
    except:
        return {"images": []}

    images = loadMoreImages(q_vec, 10, page)
    try:
        minimumScore = max(images["scores"])
    except:
        minimumScore = 1

    listOfDataFromPeers = asyncio.run(
        getImagesFromPeers(query, q_vec, queryLanguage, numberOfURLs, page,
                           minimumScore))
    if len(listOfDataFromPeers) > 0:
        listOfImagesFromHost = list(zip(images["images"], images["scores"]))
        listOfImagesFromPeers = list(
            itertools.chain(*[pack["images"] for pack in listOfDataFromPeers]))
        bigListOfImages = listOfImagesFromHost + listOfImagesFromPeers
        bigListOfImages.sort(key=lambda x: x[1])
        bigListOfImages = [
            image[0] for image in bigListOfImages if image[0] != ''
        ]
    else:
        bigListOfImages = images["images"]

    bigListOfImages = list(
        {frozenset(item.items()): item
         for item in bigListOfImages}.values())

    if page == 1:
        registerQueryInAnalytics(query)
        return {
            "corrected": escapeHTMLString(query),
            "images": bigListOfImages[:15]
        }
    else:
        return {"images": bigListOfImages[:15]}


def answerPeer(query: str, q_vec: list, queryLanguage: str, numberOfURLs: int,
               numberOfPage: int) -> jsonify:
    q_vec = np.array(ast.literal_eval("".join(q_vec)))
    registerQueryInAnalytics(query)

    urls = loadMoreUrls(q_vec, queryLanguage, numberOfURLs, numberOfPage)

    return {"urls": urls["urls"], "url_scores": urls["scores"].tolist()}


def answerPeerImages(query: str, q_vec: list, queryLanguage: str,
                     numberOfURLs: int, numberOfPage: int) -> jsonify:
    q_vec = np.array(ast.literal_eval("".join(q_vec)))
    registerQueryInAnalytics(query)

    images = loadMoreImages(q_vec, 15, numberOfPage)

    return {
        "images": images["images"],
        "images_scores": images["scores"].tolist()
    }


@app.route('/_registerPeer')
def _registerPeer():
    global listOfPeers, numberOfPeers
    peerIP = request.args.get("ip", 0, type=str)
    peerRegistryTransaction = peerRegistry.begin(write=True)
    peerRegistryTransaction.put(str(peerIP).encode('utf-8'),
                                "".encode('utf-8'),
                                overwrite=False)
    peerRegistryTransaction.commit()

    if hostname != "private":
        listOfPeers.append(peerIP)
        listOfPeers = list(set(listOfPeers))
        numberOfPeers += 1

    return jsonify(result={"listOfPeers": listOfPeers})


@app.route('/_getPeerInfo')
def _getPeerInfo():
    return jsonify(
        result={
            "uptime": time.time() - psutil.boot_time(),
            "ip": hostIP,
            "name": hostname,
            "cpu": psutil.cpu_percent(),
            "mem": psutil.virtual_memory().percent,
            "urls": FUTURE.beginTransaction().stat()["entries"],
            "images": imageDBIndex.begin().stat()["entries"]
        })


@app.route('/_getPeerList')
def _getPeerList():
    return jsonify(result={"listOfPeers": listOfPeers})


@app.route('/_getPeerInfoList')
def _getPeerInfoList():
    peerInfoList = []
    for peer in listOfPeers:
        if peer == hostIP or peer == hostname:
            peerInfoList.append({
            "uptime": time.time() - psutil.boot_time(),
            "ip": hostIP,
            "name": hostname,
            "cpu": psutil.cpu_percent(),
            "mem": psutil.virtual_memory().percent,
            "urls": FUTURE.beginTransaction().stat()["entries"],
            "images": imageDBIndex.begin().stat()["entries"]
        })
        else:
            try:
                try:
                    response = requests.get("http://" + peer + "/_getPeerInfo")
                except:
                    response = requests.get("https://" + peer + "/_getPeerInfo")
                peerInfoList.append(response.json()["result"])
            except:
                pass
    return jsonify(result={"listOfPeers": peerInfoList})


@app.route('/_retrieveImage')
@cache.cached(timeout=15, query_string=True)
def _retrieveImage():
    url = request.args.get("url", "", type=str)
    if url.startswith("//"):
        try:
            image = requests.get("http:" + url, allow_redirects=True)
        except:
            image = requests.get("https:" + url, allow_redirects=True)
    else:
        image = requests.get(url, allow_redirects=True)

    pic = Image.open(io.BytesIO(image.content))
    pic.thumbnail((480, 480), Image.LANCZOS)

    img_io = io.BytesIO()
    pic.save(img_io, 'PNG', optimize=True)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


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
    page = request.args.get("page", 1, type=int)
    return jsonify(result=answer(query, page))


@app.route("/_answerImages")
def _answerImages():
    """The method for processing form data and answering."""
    query = request.args.get("query", 0, type=str)
    page = request.args.get("page", 1, type=int)
    return jsonify(result=answerImages(query, page))


@app.route("/_answerPeer")
def _answerPeer():
    """The method for processing form data and answering."""
    query = request.args.get("query", 0, type=str)
    q_vec = request.args.get("q_vec", 0, type=str)
    queryLanguage = request.args.get("queryLanguage", 0, type=str)
    numberOfURLs = request.args.get("numberOfURLs", 0, type=int)
    numberOfPage = request.args.get("numberOfPage", 1, type=int)
    minimumScore = request.args.get("minimumScore", 0, type=float)
    result = answerPeer(query, q_vec, queryLanguage, numberOfURLs,
                        numberOfPage)
    if max(result["url_scores"]) <= minimumScore:
        return jsonify(result=result)
    else:
        return jsonify(result={
            "urls": [],
            "url_scores": []
        })  #Exception("No relevant results.")


@app.route("/_answerPeerImages")
def _answerPeerImages():
    """The method for processing form data and answering."""
    query = request.args.get("query", 0, type=str)
    q_vec = request.args.get("q_vec", 0, type=str)
    queryLanguage = request.args.get("queryLanguage", 0, type=str)
    numberOfURLs = request.args.get("numberOfURLs", 0, type=int)
    numberOfPage = request.args.get("numberOfPage", 1, type=int)
    minimumScore = request.args.get("minimumScore", 0, type=float)
    result = answerPeerImages(query, q_vec, queryLanguage, numberOfURLs,
                              numberOfPage)
    if max(result["images_scores"]) <= minimumScore:
        return jsonify(result=result)
    else:
        return jsonify(result={
            "images": [],
            "images_scores": []
        })  #Exception("No relevant results.")


@app.route("/stats")
def stats():
    return render_template("stats.html")


if __name__ == "__main__":
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host="0.0.0.0", port=port, debug=True)
