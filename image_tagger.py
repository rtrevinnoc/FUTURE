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

import numpy as np
import torch
import pickle
import os
import requests
from io import BytesIO
from torchvision import transforms
from model import EncoderCNN, DecoderRNN
from PIL import Image

vocabularyPickle = pickle.load(
    open("./models/image_tagger/data/vocab.pkl", "rb"))

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Build models
encoder = EncoderCNN(
    256).eval()  # eval mode (batchnorm uses moving mean/variance)
decoder = DecoderRNN(256, 512, len(vocabularyPickle), 1)
encoder = encoder.to(device)
decoder = decoder.to(device)

# Load the trained model parameters
encoder.load_state_dict(torch.load("./models/image_tagger/encoder-5-3000.pkl"))
decoder.load_state_dict(torch.load("./models/image_tagger/decoder-5-3000.pkl"))


def loadImage(image_path: str, transform=None):
    image = Image.open(BytesIO(requests.get(image_path).content))
    image = image.resize([224, 224], Image.LANCZOS)

    if transform is not None:
        image = transform(image).unsqueeze(0)

    return image


def tagImage(image, vocabularyPickle) -> str:
    # Image preprocessing
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])

    # Prepare an image
    image = loadImage(image, transform)
    imageTensor = image.to(device)

    # Generate an caption from the image
    feature = encoder(imageTensor)
    sampledIds = decoder.sample(feature)
    sampledIds = sampledIds[0].cpu().numpy(
    )  # (1, max_seq_length) -> (max_seq_length)

    # Convert word_ids to words
    sampledCaption = []
    for wordId in sampledIds:
        word = vocabularyPickle.idx2word[wordId]
        sampledCaption.append(word)
        if word == "<end>":
            break
    sentence = " ".join(sampledCaption[1:-1])

    # Print out the image and the generated caption
    return sentence
