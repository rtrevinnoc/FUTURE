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

import lmdb

URLDBIndex = lmdb.open("./future_urls", readonly=True)
imageDBIndex = lmdb.open("./future_images", readonly=True)
# analyticsDBIndex = lmdb.open("./future_analytics", readonly=True)

with URLDBIndex.begin() as urlDBTransaction, imageDBIndex.begin(
) as imageDBTransaction:  #, analyticsDBIndex.begin() as analyticsDBTransaction:
    print(urlDBTransaction.stat()["entries"])
    print(imageDBTransaction.stat()["entries"])
    # print(analyticsDBTransaction.stat()["entries"])
