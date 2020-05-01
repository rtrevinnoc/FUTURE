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

from typing import Callable, Iterator
import scrapy, re, gensim, h5py, string, lmdb, tldextract, json
from urllib.parse import urljoin, urlparse
from scrapy.crawler import CrawlerProcess
from nltk.tokenize import word_tokenize
from gensim.models import KeyedVectors
from polyglot.detect import Detector
from Monad import *
import numpy as np

import bson

bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode


class Vocabulary(object):
    """Simple vocabulary wrapper."""
    def __init__(self) -> None:
        self.word2idx: dict = {}
        self.idx2word: dict = {}
        self.idx: int = 0

    def addWord(self, word: str) -> None:
        if not word in self.word2idx:
            self.word2idx[word] = self.idx
            self.idx2word[self.idx] = word
            self.idx += 1

    def __call__(self, word: str) -> int:
        if not word in self.word2idx:
            return self.word2idx["<unk>"]
        return self.word2idx[word]

    def __len__(self) -> int:
        return len(self.word2idx)


from image_tagger import *


def getPropertyFromHTMLResponse(response, property: str) -> str:
    if property == "header":
        webPageProperty = response.css("h1 ::text").getall()
    elif property == "title":
        webPageProperty = response.css("title ::text").getall()
    elif property == "body":
        return " ".join(
            re.split(
                "\s+",
                u"".join(
                    response.xpath(
                        "//body/descendant-or-self::*[not(self::script)]/text()"
                    ).extract()).strip(),
                flags=re.UNICODE,
            ))
    return " ".join(
        re.split("\s+",
                 max(webPageProperty, key=len, default=""),
                 flags=re.UNICODE))


def getWebpageMeanVector(response) -> list:
    metaDescription: str = response.xpath(
        "//meta[@property='og:description']/@content").extract_first()
    if metaDescription:
        metaTitle: str = response.xpath(
            "//meta[@property='og:title']/@content").extract_first()
        if metaTitle:
            webPageTopic: str = metaTitle
        else:
            webPageHeader: str = getPropertyFromHTMLResponse(
                response, "header").strip()
            webPageTitle: str = getPropertyFromHTMLResponse(response,
                                                            "title").strip()
            webPageTopic: str = webPageHeader + ". " + webPageTitle

        return [
            getTextVectors(webPageTopic),
            metaDescription,
            Detector(metaDescription).language.name,
        ]
    else:
        webPageBody: str = getPropertyFromHTMLResponse(response,
                                                       "body").strip()
        webPageHeader: str = getPropertyFromHTMLResponse(response,
                                                         "header").strip()
        webPageTitle: str = getPropertyFromHTMLResponse(response,
                                                        "title").strip()
        wholeWebPageText: str = webPageBody + ". " + webPageHeader + ". " + webPageTitle
        return [
            getTextVectors(wholeWebPageText),
            webPageBody,
            Detector(wholeWebPageText).language.name,
        ]


class Indexer(scrapy.Spider):
    name = "indexer"
    allowed_urls = ["*"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 200,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 25,
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_ITEMS": 100,
        "REACTOR_THREADPOOL_MAXSIZE": 400,
        # Hides printing item dicts
        "LOG_LEVEL": "INFO",
        "RETRY_ENABLED": False,
        "REDIRECT_MAX_TIMES": 1,
        # Stops loading page after 5mb
        "DOWNLOAD_MAXSIZE": 100000000,
        # Grabs xpath before site finish loading
        "DOWNLOAD_FAIL_ON_DATALOSS": False,
        "DOWNLOAD_DELAY": 2.0,
        "AUTOTHROTTLE_ENABLED": True,
        "JOBDIR": "./indexer_state",
        # "SCHEDULER_PRIORITY_QUEUE": "scrapy.pqueues.DownloaderAwarePriorityQueue",
        "COOKIES_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 30,
        "AJAXCRAWL_ENABLED": True
    }

    start_urls = ["https://techcrunch.com/"]

    def parse(self, response) -> Iterator:
        webPageVector = getWebpageMeanVector(response)
        if webPageVector[1] != "":
            webPageSummary = webPageVector[0]
            url = response.request.url
            ImageDBTransaction = images.begin(write=True)
            for id, imageLink in enumerate([
                    str(urljoin(url,
                                urlparse(url).path) + imageHTMLTagSource) if
                    imageHTMLTagSource.startswith("/") else imageHTMLTagSource
                    for imageHTMLTagSource in response.xpath(
                        "//img/@src").extract()
            ]):
                try:
                    ImageDBTransaction.put(
                        encodeURLAsNumber(imageLink, ":image:" + str(id)),
                        bson.dumps({
                            "image_vec":
                            getSentenceMeanVector(
                                tagImage(imageLink,
                                         vocabularyPickle)).tostring(),
                            "word_vec":
                            np.array([
                                wordVector for wordVector in webPageSummary[0]
                                if type(wordVector) is np.ndarray
                            ]).mean(axis=0).tostring(),
                            "url":
                            imageLink,
                        }))
                except Exception as e:
                    print(e)
            ImageDBTransaction.commit()
            for id, vector in enumerate(webPageSummary[0]):
                webPageDomain: str = response.xpath(
                    "//meta[@property='og:site_name']/@content").extract_first(
                    )
                if webPageDomain:
                    webPageDomain = webPageDomain
                else:
                    webPageDomain: str = tldextract.extract(url).domain.upper()

                FUTURE.addElementToIndex(
                    encodeURLAsNumber(url, id),
                    bson.dumps({
                        "vec": np.array(vector).tostring(),
                        "vec_id": id,
                        "language": webPageVector[2],
                        "sentence": webPageSummary[1][id],
                        "url": url,
                        "domain": webPageDomain,
                        "body": webPageVector[1],
                    }))
        for href in response.css("a::attr(href)"):
            yield response.follow(href, self.parse)


if __name__ == "__main__":
    FUTURE = Monad("future_urls")
    images = lmdb.open("future_images", map_size=int(1e12), writemap=True)

    process: Callable = CrawlerProcess({
        "USER_AGENT":
        "FUTURE by Roberto Treviño Cervantes. I'am building a safer, faster and more precise Search Engine, if you do not want to be part of the index, report me to rtrevinnoc@hotmail.com"
    })
    process.crawl(Indexer)
    while True:
        try:
            process.start()
        except TimeoutError:
            print("Timed out")
