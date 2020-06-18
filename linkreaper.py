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
from Monad import *
import numpy as np

import bson

bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode


def getPropertyFromHTMLResponse(response, property: str) -> str:
    if property == "header":
        webPageProperty = response.css("h1 ::text").getall()
    elif property == "title":
        webPageProperty = response.css("title ::text").getall()
    elif property == "body":
        return " ".join(
            re.split(
                "\s+",
                u" ".join(response.css("p ::text").getall()).strip(),
                flags=re.UNICODE,
            ))
    return " ".join(
        re.split("\s+",
                 max(webPageProperty, key=len, default=""),
                 flags=re.UNICODE))


def getWebpageMeanVector(response, url) -> list:
    metaDescription: str = response.xpath(
        "//meta[@property='og:description']/@content").extract_first()
    webPageBody: str = getPropertyFromHTMLResponse(response, "body").strip()
    webPageHeader: str = getPropertyFromHTMLResponse(response, "header").strip()
    webPageTitle: str = getPropertyFromHTMLResponse(response, "title").strip()
    metaTitle: str = response.xpath("//meta[@property='og:title']/@content").extract_first()
    webPageDomain: str = response.xpath("//meta[@property='og:site_name']/@content").extract_first()

    if metaTitle:
        finalWebPageHeader: str = metaTitle
        webPageTopic: str = metaTitle
    else:
        if webPageHeader:
            finalWebPageHeader: str = webPageHeader
        else:
            finalWebPageHeader: str = webPageTitle
        webPageTopic: str = webPageHeader + ". " + webPageTitle

    if webPageTopic is None:
        wholeWebPageText: str = webPageBody + ". " + webPageHeader + ". " + webPageTitle
    else:
        wholeWebPageText: str = webPageTopic

    if not finalWebPageHeader and webPageDomain:
        finalWebPageHeader: str = webPageDomain
    else:
        finalWebPageHeader: str = tldextract.extract(url).domain.upper()

    if metaDescription:
        return [
            getSentenceMeanVector(wholeWebPageText),
            metaDescription,
            inferLanguage(wholeWebPageText),
            finalWebPageHeader,
        ]
    else:

        return [
            getSentenceMeanVector(wholeWebPageText), webPageBody,
            inferLanguage(wholeWebPageText), finalWebPageHeader
        ]


def returnDataFromImageTags(url: str, someIterable: list) -> list:
    anotherIterable = []
    for imageTag in someIterable:
        src = imageTag.xpath("@src").get()
        alt = imageTag.xpath("@alt").get()
        if src.startswith("/"):
            anotherIterable.append((str(urljoin(url, urlparse(url).path) + src), alt))
        else:
            anotherIterable.append((src, alt))
    return anotherIterable


class Indexer(scrapy.Spider):
    name = "indexer"
    allowed_urls = ["*"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 200,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 25,
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_ITEMS": 100,
        "REACTOR_THREADPOOL_MAXSIZE": 20,
        # Hides printing item dicts
        "LOG_LEVEL": "INFO",
        "RETRY_ENABLED": False,
        "REDIRECT_MAX_TIMES": 1,
        # Stops loading page after 5mb
        "DOWNLOAD_MAXSIZE": 100000000,
        # Grabs xpath before site finish loading
        "DOWNLOAD_FAIL_ON_DATALOSS": True,
        # "DOWNLOAD_DELAY": 2.0,
        "AUTOTHROTTLE_ENABLED": False,
        # "JOBDIR": "./indexer_state",
        "SCHEDULER_PRIORITY_QUEUE": "scrapy.pqueues.DownloaderAwarePriorityQueue",
        "COOKIES_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 120,
        "SCHEDULER_DISK_QUEUE": 'scrapy.squeues.PickleFifoDiskQueue',
        "SCHEDULER_MEMORY_QUEUE": 'scrapy.squeues.FifoMemoryQueue',
        "AJAXCRAWL_ENABLED": True
    }

    start_urls = ["https://techcrunch.com/"]

    def parse(self, response) -> Iterator:
        url = response.request.url
        webPageVector = getWebpageMeanVector(response, url)
        print(webPageVector[3])
        if webPageVector[0].size == 50:
            webPageSummaryVector = webPageVector[0]
            listOfImagesAndDescriptions = returnDataFromImageTags(
                url, response.xpath("//img"))
            ImageDBTransaction = images.begin(write=True)
            for id, imageLink, imageDescription in returnUnpackedListOfTrigrams(
                    enumerate(listOfImagesAndDescriptions)):
                imageDescriptionVectorPreliminar = getSentenceMeanVector(
                    imageDescription)
                if imageDescriptionVectorPreliminar.size == 50:
                    imageDescriptionVector = np.array([
                        imageDescriptionVectorPreliminar,
                        webPageSummaryVector
                    ]).mean(axis=0)
                else:
                    imageDescriptionVector = webPageSummaryVector
                try:
                    ImageDBTransaction.put(
                        encodeURLAsNumber(imageLink, ":image:" + str(id)),
                        bson.dumps({
                            "vec": imageDescriptionVector.tostring(),
                            "url": imageLink,
                        }))
                except Exception as e:
                    print(e)
            ImageDBTransaction.commit()
            URLDBTransaction = FUTURE.beginTransaction(writePermission=True)
            FUTURE.addElementToIndex(
                encodeURLAsNumber(url, 1),
                bson.dumps({
                    "vec": webPageSummaryVector.tostring(),
                    "language": webPageVector[2],
                    "body": webPageVector[1],
                    "header": webPageVector[3],
                    "url": url
                }), URLDBTransaction)
            URLDBTransaction.commit()
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
    process.start()
