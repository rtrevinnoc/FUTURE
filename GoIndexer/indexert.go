// Copyright (c) 2020 Roberto Treviño Cervantes

// #########################################################################
// #                                                                       #
// # This file is part of FUTURE (Powered by Monad).                       #
// #                                                                       #
// # FUTURE is free software: you can redistribute it and/or modify        #
// # it under the terms of the GNU General Public License as published by  #
// # the Free Software Foundation, either version 3 of the License, or     #
// # (at your option) any later version.                                   #
// #                                                                       #
// # FUTURE is distributed in the hope that it will be useful,             #
// # but WITHOUT ANY WARRANTY; without even the implied warranty of        #
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
// # GNU General Public License for more details.                          #
// #                                                                       #
// # You should have received a copy of the GNU General Public License     #
// # along with FUTURE.  If not, see <https://www.gnu.org/licenses/>.      #
// #                                                                       #
// #########################################################################

package main

import (
	"fmt"
	"strings"

	"github.com/gocolly/colly/v2"
	"github.com/gocolly/colly/v2/extensions"
)

func main() {
	c := colly.NewCollector(
		colly.Async(true),
	)

	c.Limit(&colly.LimitRule{DomainGlob: "*", Parallelism: 10})
	extensions.RandomUserAgent(c)

	c.OnRequest(func(r *colly.Request) {
		fmt.Println("Visiting", r.URL, "as", r.Headers.Get("User-Agent"))
	})

	c.OnXML("//meta[@property='og:description']/@content", func(e *colly.XMLElement) {
		fmt.Println(e.Text)
	})

	c.Visit("http://rtrevinnoc.github.io/")
	c.Wait()
}
