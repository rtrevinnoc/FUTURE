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
	"strconv"
	"net/url"
	"io/ioutil"
	"math"

	"github.com/gocolly/colly/v2"
	"github.com/gocolly/colly/v2/extensions"
	"gopkg.in/neurosnap/sentences.v1/english"
	"labix.org/v2/mgo/bson"
)

func RemoveIndex(s []string, index int) []string {
	return append(s[:index], s[index+1:]...)
}

func readlines(file string) ([]string) {
	content, _ := ioutil.ReadFile(file)
	return strings.Split(string(content), "\n")
}

func loadGloveModel(file string) (map[string][]float32) {
	gloveModel := map[string][]float32{}
	literalVectors := RemoveIndex(readlines(file), 0)
	for _, literalVector := range literalVectors {
		tokens := strings.Split(literalVector, " ")
		gloveVector := []float32{}
		for index, component := range tokens {
			if index > 0 {
				preliminar, _ := strconv.ParseFloat(component, 32)
				gloveVector = append(gloveVector, float32(preliminar))
			}
		}
		gloveModel[tokens[0]] = gloveVector
	}
	return gloveModel
}

func addVectors(vectors [][]float32) ([]float32) {
	resultant := []float32{}
	for index, _ := range vectors[0] {
		var result float32
		for _, vector := range vectors {
			result += vector[index]
		}
		resultant = append(resultant, result)
	}
	return resultant
}

func divideVector(vector []float32, divisor float32) ([]float32) {
	resultant := []float32{}
	for _, component := range vector {
		resultant = append(resultant, component / divisor)
	}
	return resultant
}

func getSentenceMeanVector(sentence string) ([]float32) {
	if sentence == "" {
		return []float32{}
	}
	words := strings.Split(strings.ToLower(sentence), " ")
	wordVectors := [][]float32{}
	for _, word := range words {
		wordVectors = append(wordVectors, gloveModel[word])
	}
	return divideVector(addVectors(wordVectors), float32(len(words)))
}

func encodeURLAsNumber(url string, id int) (string) {
	text := string(id) + ":" + url
	var asciiCodesSum float64
	for index, code := range text {
		index -= len(text) + 1
		asciiCodesSum += float64(code) * math.Pow(128.0, float64(index))
	}
	return strings.Replace(strconv.FormatFloat(asciiCodesSum, 'f', -1, 64), ".", "8", 1)
}

var stopWords = readlines("stop_words.txt")
var gloveModel = loadGloveModel("glove.6B/glove.6B.50d.txt")
var tokenizer, _ = english.NewSentenceTokenizer(nil)

func saveDataFromWebPage(url url.URL, metaSiteName, metaTitle, metaDescription, webPageTitle, webPageHeader, webPageBody string) {
	hostname := url.Hostname()
	preliminarVectorElementsList := []string{}

	if metaSiteName != "" {
		preliminarVectorElementsList = append(preliminarVectorElementsList, metaSiteName)
	} else {
		preliminarVectorElementsList = append(preliminarVectorElementsList, hostname)
	}

	if metaTitle != "" {
		preliminarVectorElementsList = append(preliminarVectorElementsList, metaTitle)
	} else {
		preliminarVectorElementsList = append(preliminarVectorElementsList, webPageTitle + webPageHeader)
	}

	if metaDescription != "" {
		preliminarVectorElementsList = append(preliminarVectorElementsList, metaDescription)
	} else {
		preliminarVectorElementsList = append(preliminarVectorElementsList, webPageBody)
	}

	preliminarVectorElement := strings.Join(preliminarVectorElementsList, " ")
	sentences := tokenizer.Tokenize(preliminarVectorElement)

	for index, sentence := range sentences {
		sentence := sentence.Text

		i := strings.LastIndex(sentence, ".")
		if i > 0 {
			sentence = sentence[:i] + strings.Replace(sentence[i:], ".", "", 1)
		}
		sentence = strings.Replace(sentence, ",", "", -1)
		sentence = strings.Replace(sentence, ";", "", -1)
		sentence = strings.Replace(sentence, ":", "", -1)
		sentence = strings.Replace(sentence, "'", "", -1)
		sentence = strings.Replace(sentence, "(", "", -1)
		sentence = strings.Replace(sentence, ")", "", -1)
		sentence = strings.Replace(sentence, "[", "", -1)
		sentence = strings.Replace(sentence, "]", "", -1)
		sentence = strings.Replace(sentence, "{", "", -1)
		sentence = strings.Replace(sentence, "}", "", -1)
		sentence = strings.Replace(sentence, `"`, "", -1)
		sentence = strings.Replace(sentence, `¿`, "", -1)
		sentence = strings.Replace(sentence, `?`, "", -1)
		sentence = strings.Replace(sentence, `¡`, "", -1)
		sentence = strings.Replace(sentence, `!`, "", -1)

		webPagePointer := FUTUREIndexedWebpagePointer{
			vectorToString(getSentenceMeanVector(sentence)),
			index,
			sentence,
		}

		webPagePointerBinaryDictionary, _ := bson.Marshal(webPagePointer)
	}
}

type FUTUREIndexedWebpage struct {
	Url string
	Domain string
	Body string
	Language string

}

type FUTUREIndexedWebpagePointer struct {
	Vec string
	Vec_id int
	Sentence string
}

func vectorToString(vec []float32) (string) {
	resultant := []string{}
	for _, component := range vec {
		resultant = append(resultant, strconv.FormatFloat(float64(component), 'f', -1, 32))
	}
	return strings.Join(resultant, " ")
}

func main() {
	var metaSiteName, metaTitle, metaDescription, webPageTitle, webPageHeader, webPageBody string
	var url url.URL

	c := colly.NewCollector(
		colly.Async(true),
	)

	c.Limit(&colly.LimitRule{DomainGlob: "*", Parallelism: 10})
	extensions.RandomUserAgent(c)

	c.OnRequest(func(r *colly.Request) {
		fmt.Println("Visiting", r.URL, "as", r.Headers.Get("User-Agent"))
		url = *r.URL
	})

	c.OnXML("//meta[@property='og:description']/@content", func(e *colly.XMLElement) {
		metaDescription = strings.TrimSpace(e.Text)
	})


	c.OnXML("//meta[@property='og:title']/@content", func(e *colly.XMLElement) {
		metaTitle = strings.TrimSpace(e.Text)
	})

	c.OnXML("//meta[@property='og:description']/@content", func(e *colly.XMLElement) {
		metaSiteName = strings.TrimSpace(e.Text)
	})

	c.OnHTML("h1", func(e *colly.HTMLElement) {
		webPageHeader = strings.TrimSpace(e.Text)
	})

	c.OnHTML("title", func(e *colly.HTMLElement) {
		webPageTitle = strings.TrimSpace(e.Text)
	})

	webPageBodyElement := []string{}
	c.OnHTML("p", func(e *colly.HTMLElement) {
		webPageBodyElement = append(webPageBodyElement, e.Text)
	})
	webPageBody = strings.Join(webPageBodyElement, " ")

	c.OnHTML("img[src]", func(e *colly.HTMLElement) {
		fmt.Println("@@@@@@@@@@@@@@@@@@@@@@@@@@")
		fmt.Println(e.Attr("src"))
		fmt.Println("@@@@@@@@@@@@@@@@@@@@@@@@@@")
	})

	// Find and visit all links
	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		e.Request.Visit(e.Attr("href"))
	})

	c.OnScraped(func(r *colly.Response) {
		saveDataFromWebPage(url, metaSiteName, metaTitle, metaDescription, webPageTitle, webPageHeader, webPageBody)
	})

	c.Visit("http://rtrevinnoc.github.io/")
	c.Wait()
}
