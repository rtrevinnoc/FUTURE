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

from typing import Generator, Iterable, Any, Tuple, Iterator, List, Callable
import base64, h5py, gensim, re, spacy, folium, html
from geopy.geocoders import Nominatim
from nltk.tokenize import sent_tokenize
from gensim.models import KeyedVectors
import numpy as np
from scipy.spatial import distance
from itertools import tee, islice, chain
from nltk.corpus import wordnet
from SPARQLWrapper import SPARQLWrapper, JSON

import os.path, os, shutil, json, random, smtplib, sys, socket, re, mimetypes, datetime, pyqrcode, lmdb, hnswlib, time, bson, requests
bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

gloveVectors = KeyedVectors.load_word2vec_format("./glove.6B/glove.6B.50d.txt",
                                                 binary=False)
gloveVectors.init_sims()
normalizedGloveVectors: np.ndarray = gloveVectors.syn0norm
gloveVocabulary: dict = gloveVectors.vocab

stopWords: List[str] = [
    x.decode("utf-8").rstrip()
    for x in list(h5py.File("stoplist.hdf5", "r")["words"])
]

spacyModel: Callable = spacy.load("en_core_web_sm")


def cleanDBPediaResourceName(name: str) -> str:
    """
      Parameters:
      1. name - preliminar name of the resource to find

      What the function does?
      -----------------------
      It simply preprocesses a name to find its corresponding DBPedia locator

      Returns:
      ---------
      A DBPedia resource URL
   """

    if name.startswith("#"):
        return "http://dbpedia.org/resource/" + name.split(
            "-")[1].title().replace(" ", "_")


def getTaggedNames(string: str) -> list:
    """
      Parameters:
      1. string - a piece of text

      What the function does?
      -----------------------
      It locates the name that are tagged with an "@" in a piece of text, for the social network.

      Returns:
      ---------
      A list of names tagged in the text, with the "@" prefix removed.
   """

    return [
        word.strip(",.-@") for word in string.split(" ")
        if word.startswith("@")
    ]


def appendIfNotInList(element: Any, iterable: list) -> list:
    """
      Parameters:
      1. element - any object
      2. iterable - an iterable object

      What the function does?
      -----------------------
      It appends <<element>> to <<iterable>> if <<element>> is not already in <<iterable>>

      Returns:
      ---------
      <<iterable>> with <<element> appended
   """

    if element not in iterable:
        iterable.append(element)
    return iterable


def encodeTo64Bytes(string: str) -> bytes:
    return base64.b64encode(string.encode("utf-8"))


def decodeToUnicodeString(bytestring: bytes) -> str:
    return base64.b64decode(bytestring).decode("utf-8")


def divideInTrigrams(someIterable: Iterable[Any]) -> Iterable[Iterable[Any]]:
    """
      Parameters:
      1. someIterable - an iterable object

      What the function does?
      -----------------------
      Divides <<iterable>> in windows of 3, such as [1,2,3] becoming [[None, 1, 2], [1,2,3], [2, 3, None]]

      Returns:
      ---------
      A decomposed <<iterable>> as an iterable composed of [previous, current, next] for each <<current> in <<iterable>>
   """

    prevs, items, nexts = tee(someIterable, 3)
    return zip(chain([None], prevs), items,
               chain(islice(nexts, 1, None), [None]))


def returnInPairsIfItemsContainUnderscore(someIterable: Iterable[str]
                                          ) -> Iterator[str]:
    """
      Parameters:
      1. someIterable - an iterable object

      What the function does?
      -----------------------
      Divides <<iterable>> in pairs for each element if the current element contains an underscore (_), such as returning ["hi", ["current_", "hello"], "hello"] for ["hi", "current_", "hello"]

      Returns:
      ---------
      An iterable where elements containing an underscore are joined in a list with its next contiguous element.
   """

    iterator: Iterator[str] = iter(someIterable)
    for element in iterator:
        if element.endswith("_"):
            nextElement: str = next(iterator)
            yield (element + nextElement.replace(" ", "_",
                                                 (nextElement.count(" ") - 1)))
        else:
            yield element


def tokenizeSentence(text: str) -> List[str]:
    """
      Parameters:
      1. text - a string

      What the function does?
      -----------------------
      Divides <<text>> in tokens for use in FUTURE, while intelligently joining phrasal nouns, such as "Rage Agains The Machine"

      Returns:
      ---------
      Returns a list of strings of each token
   """

    parsedText: Any = spacyModel(text)
    list(parsedText.noun_chunks)

    for nounPhrase in list(parsedText.noun_chunks):
        nounPhrase.merge(nounPhrase.root.tag_, nounPhrase.root.lemma_,
                         nounPhrase.root.ent_type_)

    stringAndType: List[Tuple[Any, Any]] = [(token.text, token.pos_)
                                            for token in parsedText]
    newTokens: List[str] = []
    for (previous, current, _) in divideInTrigrams(stringAndType):
        try:
            if current[1] == "PROPN" and " " in current[0]:
                newTokens.append(current[0].replace(" ", "_"))
            elif current[1] == "PUNCT":
                pass
            elif current[1] == "NOUN":
                newParsedText = spacyModel(current[0])
                for (innerPrevious, innerCurrent, _) in divideInTrigrams([
                    (token.text, token.pos_) for token in newParsedText
                ]):
                    if innerCurrent[1] == "PROPN" and innerPrevious[
                            1] == "PROPN":
                        newTokens.pop(-1)
                        newTokens.append(innerPrevious[0] + "_" +
                                         innerCurrent[0])
                    elif innerCurrent[0] == newTokens[-1]:
                        newTokens.pop(-1)
                else:
                    newTokens.append(innerCurrent[0])
            elif current[0].startswith("'") or current[0].startswith("n'"):
                newTokens.pop(-1)
                newTokens.append(previous[0] + current[0])
            else:
                newTokens.append(current[0])
        except:
            newTokens.append(current[0])

    newTokensWithoutUnderscore: List[str] = [
        x.replace(" ", "_")
        for x in returnInPairsIfItemsContainUnderscore(newTokens)
    ]
    lastPass: List[str] = []
    for (previous, current, _) in divideInTrigrams([
            token.text
            for token in spacyModel(" ".join(newTokensWithoutUnderscore))
    ]):
        try:
            if current.startswith(previous) and current != previous:
                lastPass.append(current.replace(previous + "_", "", 1))
            else:
                lastPass.append(current)
        except:
            lastPass.append(current)
    return [word for word in lastPass if not word in stopWords]


def getWordChunkVector(sentence: str) -> np.array:
    words: List[str] = tokenizeSentence(sentence)
    normalizedWordVectors = []
    for word in words:
        try:
            normalizedWordVectors.append(
                normalizedGloveVectors[gloveVocabulary[word].index])
        except:
            pass
    return gensim.matutils.unitvec(
        np.array(normalizedWordVectors).mean(axis=0)).astype(np.float32)


def getSentenceMeanVector(sentence: str) -> np.array:
    words = tokenizeSentence(sentence)
    normalizedWordVectors = []
    for word in words:
        word = re.sub(r"\W", "", word)
        try:
            normalizedWordVectors.append(
                normalizedGloveVectors[gloveVocabulary[word].index])
        except:
            try:
                internalNormalizedWordVectors = []
                for x in word.split("_"):
                    internalNormalizedWordVectors.append(
                        normalizedGloveVectors[gloveVocabulary[x].index])
                    normalizedWordVectors.append(
                        gensim.matutils.unitvec(
                            np.array(internalNormalizedWordVectors).mean(
                                axis=0)).astype(np.float32))
            except:
                try:
                    normalizedWordVectors.append(
                        getWordChunkVector(
                            wordnet.synsets(word)[0].definition()))
                except:
                    try:
                        normalizedWordVectors.append(
                            getWordChunkVector(getDefinitionFromDBPedia(word)))
                    except:
                        pass
    return gensim.matutils.unitvec(
        np.array(normalizedWordVectors).mean(axis=0)).astype(np.float32)


locationVector: np.array = getSentenceMeanVector(
    "location country city place landmark land monument sculpture building structure"
)


def getTextVectors(text: str) -> list:
    sentences: List[str] = sent_tokenize(text)
    tokenizedSentences: List[List[str]] = [
        tokenizeSentence(sentence) for sentence in sentences
    ]
    normalizedWordVectors = []
    for words in tokenizedSentences:
        internalNormalizedWordVectors = []
        for word in words:
            word = word.lower()
            try:
                internalNormalizedWordVectors.append(
                    normalizedGloveVectors[gloveVocabulary[word].index])
            except:
                try:
                    moreInternalNormalizedVectors = []
                    for x in word.split("_"):
                        moreInternalNormalizedVectors.append(
                            normalizedGloveVectors[gloveVocabulary[x].index])
                        internalNormalizedWordVectors.append(
                            gensim.matutils.unitvec(
                                np.array(moreInternalNormalizedVectors).mean(
                                    axis=0)).astype(np.float32))
                except:
                    try:
                        internalNormalizedWordVectors.append(
                            getSentenceMeanVector(
                                wordnet.synsets(word)[0].definition()))
                    except:
                        try:
                            internalNormalizedWordVectors.append(
                                getSentenceMeanVector(
                                    getDefinitionFromDBPedia(word)))
                        except:
                            pass
        if internalNormalizedWordVectors != []:
            normalizedWordVectors.append(
                np.array(internalNormalizedWordVectors).mean(axis=0))
        else:
            normalizedWordVectors.append("None")
    return [normalizedWordVectors, sentences]


def encodeURLAsNumber(url: str, id: Any) -> bytes:
    """
      Parameters:
      1. url - a string
      2. id - a string or a number-like object

      What the function does?
      -----------------------
      Converts an url into a unique float number encoded as a bytestring

      Returns:
      ---------
      Returns a bytestring
   """

    text = str(id) + ":" + url
    text = [code for code in text.encode("ascii")]
    return (str(
        sum([y * (128**x) for x, y in enumerate(text, start=-len(text) + 1)
             ])).replace(".", "8").encode("utf-8"))


def isLocation(vec: np.array) -> bool:
    dist: float = distance.cosine(vec, locationVector)
    if dist >= 0.3:
        return True
    else:
        return False


def preprocessSentece(sentence: str) -> str:
    if ("is the" in sentence.lower() or "are the" in sentence.lower()
            or "show me" in sentence.lower()
            or "show me the" in sentence.lower()):
        blackList: Tuple[str, ...] = (
            "who",
            "was",
            "where",
            "born",
            "when",
            "which",
            "what",
            "is",
            "a",
            "die",
            "dead",
            "died",
            "did",
            "does",
            "do",
            "why",
            "are",
            "the",
            "me",
            "an",
        )
    else:
        blackList: Tuple[str, ...] = (
            "who",
            "was",
            "where",
            "born",
            "when",
            "which",
            "what",
            "is",
            "a",
            "die",
            "dead",
            "died",
            "did",
            "does",
            "do",
            "why",
            "are",
            "an",
        )
    whiteList: List[str] = sentence.lower().replace("?", "").split(" ")
    return " ".join([word for word in whiteList
                     if word not in blackList]).title()


def getResourceFromDBPedia(query: str) -> dict:
    try:
        try:
            sparql.setQuery(
                """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            SELECT ?s WHERE {
              {
                ?s rdfs:label "%(query)s"@en ;
                   a owl:Thing .
              }
              UNION
              {
                ?altName rdfs:label "%(query)s"@en ;
                         dbo:wikiPageRedirects ?s .
              }
            }""" % locals())
            return {
                "resource":
                sparql.query().convert()["results"]["bindings"][0]["s"]
                ["value"],
                "verification":
                True
            }
        except:
            queryLowercase = query.lower()
            sparql.setQuery(
                """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            SELECT ?s WHERE {
              {
                ?s rdfs:label "%(queryLowercase)s"@en ;
                   a owl:Thing .
              }
              UNION
              {
                ?altName rdfs:label "%(queryLowercase)s"@en ;
                         dbo:wikiPageRedirects ?s .
              }
            }""" % locals())
        return {
            "resource":
            cleanDBPediaResourceName(sparql.query().convert()["results"]
                                     ["bindings"][0]["s"]["value"]),
            "verification":
            True
        }
    except:
        return {
            "resource":
            "http://dbpedia.org/resource/" +
            preprocessSentece(query).capitalize().replace(" ", "_"),
            "verification":
            True
        }


def getAbstractFromDBPedia(query: str) -> str:
    try:
        sparql.setQuery("""
         select str(?desc)
            where {
              <%s> <http://dbpedia.org/ontology/abstract> ?desc
              FILTER (langMatches(lang(?desc),"en"))
            }
         """ % getResourceFromDBPedia(preprocessSentece(query))["resource"])
        return sparql.query().convert(
        )[u"results"][u"bindings"][0][u"callret-0"][u"value"]
    except:
        return "We are still working to provide the full FUTURE experience, of which a summary of the information in the webpages retrieved is crucial, however, being at a research stage, we suggest to select the LINKS section in the sidebar, using the button on the upper-right corner."


def getDefinitionFromDBPedia(word: str) -> Any:
    try:
        sparql.setQuery("""
         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

         select str(?desc)
            where {
              <%s> rdfs:comment ?desc
              FILTER (langMatches(lang(?desc),"en"))
            }
         """ % getResourceFromDBPedia(preprocessSentece(word))["resource"])
        return sparql.query().convert(
        )[u"results"][u"bindings"][0][u"callret-0"][u"value"]
    except:
        return None


def isPlace(query: str) -> bool:
    sparql.setQuery("""
      select ?type where {
         <%s> a ?type
      }
      """ % getResourceFromDBPedia(query)["resource"])
    try:
        for x in sparql.query().convert()["results"]["bindings"]:
            if x["type"]["value"] == "http://dbpedia.org/ontology/Place":
                return True
    except:
        return False


def createMap(query: str) -> str:
    processed: str = preprocessSentece(query)
    geolocator = Nominatim()
    location = geolocator.geocode(processed)
    mapObject = folium.Map(location=[location.latitude, location.longitude])
    mapObject.add_child(
        folium.Marker([location.latitude, location.longitude],
                      popup=location.address))
    return mapObject._repr_html_().replace(
        '<div style="position:relative;width:100%;height:0;padding-bottom:60%;">',
        '').replace("</iframe></div>", "</iframe>")


def getMap(alternateQuery: str, query: str) -> str:
    try:
        try:
            return createMap(query)
        except:
            return createMap(alternateQuery)
    except:
        return ""


def escapeHTMLString(string: str) -> str:
    # Prevent failure if string is None
    try:
        return html.escape(string)
    except:
        return None


class Monad():
    def __init__(self, database: str, mapSize=int(1e12)):
        np.random.seed(0)
        self.database = lmdb.open(database, map_size=mapSize, writemap=True)

    def loadIndex(self,
                  indexName: str,
                  maxElements=100000,
                  dimensions=50,
                  efConstruction=100):
        self.indexName = indexName
        self.index = hnswlib.Index(space="cosine", dim=dimensions)
        self.index.load_index(indexName + ".bin", max_elements=maxElements)
        self.index.set_ef(efConstruction)

    def saveIndex(self):
        self.index.save_index(self.indexName + ".bin")

    def createIndex(self,
                    indexName: str,
                    maxElements=100000,
                    dimensions=50,
                    efConstruction=200):
        self.indexName = indexName
        self.index = hnswlib.Index(space="cosine", dim=dimensions)
        self.index.init_index(max_elements=maxElements,
                              ef_construction=efConstruction,
                              M=16)

    def compileIndex(self):
        with self.database.begin() as databaseTransaction:
            print(databaseTransaction.stat()["entries"])
            databaseSelector = databaseTransaction.cursor()
            for key, value in databaseSelector:
                try:
                    self.index.add_items(
                        np.array([
                            np.frombuffer(bson.loads(value)["vec"],
                                          dtype="float32")
                        ]),
                        np.array([int(key.decode("utf-8"))]),
                    )
                except:
                    pass

    def addElementToIndex(self, key, element):
        with self.database.begin(write=True) as databaseTransaction:
            databaseTransaction.put(key, element)

    def searchIndex(self, term: np.ndarray, number):
        vectorIds, vectorScores = self.index.knn_query(term, k=number)
        with self.database.begin() as databaseTransaction:
            return {
                "results": [
                    bson.loads(databaseTransaction.get(str(x).encode("utf-8")))
                    for x in vectorIds[0]
                ],
                "vectorIds":
                vectorIds,
                "vectorScores":
                vectorScores
            }


# newTokenizedSentences = []

# for sentence in getAbstractFromDBPedia("statue of liberty").split("."):
#     newTokens = []
#     for token in tokenizeSentence(sentence.strip()):
#         tokenWithoutUnderscore = token.replace("_", " ")
#         sentenceWithoutTokenWithoutUnderscore = sentence.replace("_", " ").split(tokenWithoutUnderscore, 1)
#         tokenInbetweenWords = sentenceWithoutTokenWithoutUnderscore[0]
#         newTokens.append(tokenInbetweenWords.strip())
#         newTokens.append(token)
#         sentence = sentence.replace(tokenInbetweenWords + tokenWithoutUnderscore, "")
#     newTokenizedSentences.append(newTokens)

# # print(newTokenizedSentences[1])

# for newTokenizedSentence in newTokenizedSentences:
#     insideInternalSentence = False
#     moreNewTokenizedSentences = []
#     internalTokenizedSentences = []
#     for token in newTokenizedSentence:
#         if token.startswith(",") and insideInternalSentence == True:
#             insideInternalSentence = False
#         elif token.startswith(",") and insideInternalSentence == False:
#             insideInternalSentence = True
#         elif "(" in token:
#             insideInternalSentence = True
#             token = token.replace("(", "")
#         elif ")" in token:
#             insideInternalSentence = False
#             token = token.replace(")", "")

#         if insideInternalSentence == True:
#             if token != "":
#                 internalTokenizedSentences.append( token.replace(",", "").strip() )
#         else:
#             if internalTokenizedSentences != []:
#                 moreNewTokenizedSentences.append(internalTokenizedSentences)
#             if token != "":
#                 moreNewTokenizedSentences.append(token)
#             internalTokenizedSentences = []
#     if internalTokenizedSentences != []:
#         moreNewTokenizedSentences.append(internalTokenizedSentences)
#     print(moreNewTokenizedSentences)

# # print(internalTokenizedSentences)
