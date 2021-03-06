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

import lmdb, base64, hnswlib, bson
import numpy as np
from Monad import Monad, getSentenceMeanVector

bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode

futureURLs = Monad("future_urls")
futureURLs.createIndex("FUTURE_url_vecs")
futureURLs.compileIndex()

hnswImagesLookup = hnswlib.Index(space="cosine", dim=50)
hnswImagesLookup.init_index(max_elements=1000000, ef_construction=200, M=16)
hnswImagesLookup.set_ef(100)
imageDBIndex = lmdb.open("./future_images", readonly=True)
with imageDBIndex.begin() as imageDBTransaction:
    imageDBSelector = imageDBTransaction.cursor()
    for key, value in imageDBSelector:
        value = bson.loads(value)
        try:
            hnswImagesLookup.add_items(
                np.array([np.frombuffer(value["vec"], dtype="float32")]),
                np.array([int(key.decode("utf-8"))]),
            )
        except:
            pass

#search = futureURLs.searchIndex(getSentenceMeanVector("web hosting"), 5, 1)
futureURLs.saveIndex()

#labels, distances = hnswImagesLookup.knn_query(
#    getSentenceMeanVector("web hosting"), k=5)
#print(labels)
#print(distances)
hnswImagesLookup.save_index("FUTURE_images_vecs.bin")
