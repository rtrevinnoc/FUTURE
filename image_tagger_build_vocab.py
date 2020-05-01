# Copyright 2017 Yunjey Choi.
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import nltk
import pickle
import argparse
from collections import Counter
from pycocotools.coco import COCO


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


def buildVocab(json: str, threshold: int):
    """Build a simple vocabulary wrapper."""
    coco = COCO(json)
    counter = Counter()
    ids = coco.anns.keys()
    for number, id in enumerate(ids):
        caption = str(coco.anns[id]["caption"])
        tokens = nltk.tokenize.word_tokenize(caption.lower())
        counter.update(tokens)

        if (number + 1) % 1000 == 0:
            print("[{}/{}] Tokenized the captions.".format(
                number + 1, len(ids)))

    # If the word frequency is less than 'threshold', then the word is discarded.
    words = [word for word, count in counter.items() if count >= threshold]

    # Create a vocab wrapper and add some special tokens.
    vocab = Vocabulary()
    vocab.addWord("<pad>")
    vocab.addWord("<start>")
    vocab.addWord("<end>")
    vocab.addWord("<unk>")

    # Add the words to the vocabulary.
    for word in words:
        vocab.addWord(word)
    return vocab


def main(args):
    vocab = buildVocab(
        json="./models/image_tagger/data/annotations/captions_train2014.json",
        threshold=4,
    )
    vocabPath = "./models/image_tagger/data/vocab.pkl"
    with open(vocabPath, "wb") as f:
        pickle.dump(vocab, f)
    print("Total vocabulary size: {}".format(len(vocab)))
    print("Saved the vocabulary wrapper to '{}'".format(vocabPath))
