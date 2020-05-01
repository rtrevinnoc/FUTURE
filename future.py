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
from translator_esp_eng import *
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
    confirm_login,
    fresh_login_required,
)
from chatbot import *
import os.path, os, shutil, json, random, smtplib, sys, socket, re, mimetypes, datetime, pyqrcode, lmdb, hnswlib, time, bson, requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    url_for,
    send_from_directory,
    flash,
    abort,
    jsonify,
    escape,
    make_response,
)
from forms import *
# from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename
from flask_scrypt import (
    generate_random_salt,
    generate_password_hash,
    check_password_hash,
)
from base64 import b64decode
from flask_mail import Mail, Message
from pymongo import MongoClient
from symspellpy.symspellpy import SymSpell, Verbosity
from polyglot.detect import Detector
from bs4 import BeautifulSoup
from naive_bayes_chatbot_classifier import *

bson.loads = bson.BSON.decode
bson.dumps = bson.BSON.encode

global app, mail, accounts, hnswImagesLookup, imageDBIndex, spellChecker, dirname, queryClassifier
dirname = os.path.dirname(__file__)
client = MongoClient("localhost", 27017)
db = client["Prometheus"]
accounts = db.accounts
app = Flask(__name__, static_url_path="")
app.config.from_object("config")
app.config.update(
    MAIL_SERVER=app.config['MAIL_SERVER'],
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=app.config['MAIL_USERNAME'],
    MAIL_PASSWORD=app.config['MAIL_PASSWORD'],
)
mail = Mail(app)
np.random.seed(0)
hnswImagesLookup = hnswlib.Index(space="cosine", dim=50)
hnswImagesLookup.load_index("FUTURE_images_vecs.bin", max_elements=100000)
hnswImagesLookup.set_ef(100)
imageDBIndex = lmdb.open("future_images", map_size=int(1e12), writemap=True)
FUTURE = Monad("future_urls")
FUTURE.loadIndex("FUTURE_url_vecs")
spellChecker = SymSpell(
    2,
    7)  # PARAMETERS INDICATE (MAX EDIT DISTANCE DICTIONARY AND PREFIX LENGTH)
spellChecker.load_dictionary(
    "./frequency_dictionary_en_82_765.txt", 0, 1
)  # LAST TWO PARAMETERS ARE (COLUMN TERM, FREQUENCY TERM) LOCATIONS IN DICTIONARY FILE
loginManager = LoginManager(app)
loginManager.init_app(app)

trainData = [
    "I love you",
    "how are you?",
    "what is a tesseract?",
    "when did Einstein die?",
    "How are you feeling?",
    "When did you write that?",
    "what is that?",
    "I don't like that",
    "where was Proust born?",
    "what is a computer?",
    "who is the president?",
    "dog",
    "computer",
    "ken miles",
    "hello",
    "hi",
]
trainLabels = [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0]
queryClassifier = QueryClassifier(np.unique(trainLabels))
queryClassifier.train(trainData, trainLabels)


class User(UserMixin):
    def __init__(self, name: str):
        self.name = name
        user = accounts.find_one({"name": name})
        if user:
            self.password = user["password"]
            self.salt = user["salt"]
        else:
            return None

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.name

    def check_password(self, password_hash: bytes):
        return check_password_hash(password_hash, self.password, self.salt)

    def register(self, password: str, email: str):
        self.password = password
        self.email = email
        salt = generate_random_salt()
        accounts.insert_one({
            "name":
            self.name,
            "password":
            generate_password_hash(self.password, salt),
            "email":
            self.email,
            "salt":
            salt,
        })
        msg = Message(
            self.name + ", your FUTURE account has been created",
            sender="rtrevinnoc@hotmail.com",
            recipients=[self.email],
        )
        msg.html = open("./templates/confirmation.html").read()
        mail.send(msg)

    @loginManager.user_loader
    def load_user(name: str):
        user = accounts.find_one({"name": name})
        if not user:
            return None
        return User(user["name"])

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        sign = SignForm()
        error = None
        if (sign.validate_on_submit()
                and sign.password.data == sign.confirmPassword.data
                and not accounts.find_one({"name": sign.name.data})):
            user = User(sign.name.data)
            user.register(sign.password.data, sign.email.data)
            login_user(user, remember=True)
            return redirect("/")
        return render_template("signup.html", login=sign, error=error)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect("/")
        sign = LoginForm()
        error = None
        if sign.validate_on_submit():
            try:
                user = User(sign.name.data)
                if user.check_password(str.encode(sign.password.data)):
                    login_user(user, remember=True)
                    return redirect("/")
                else:
                    error = "Oops! Incorrect password"
            except:
                error = "Oops! That user is not registered"
        return render_template("login.html", login=sign, error=error)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect("/")


@app.route("/particles_white.json")
def particlesWhite():
    return send_from_directory("static/js/", "particles_white.json")


@app.route("/particles_black.json")
def particlesBlack():
    return send_from_directory("static/js/", "particles_black.json")


@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return render_template("index.html", name=current_user.get_id())
    return render_template("index.html", name=None)


@app.route("/_answer")
def _answer():
    """The method for processing form data and answering."""
    start = time.time()
    query = request.args.get("query", 0, type=str)
    queryBeforePreprocessing = query
    queryLanguage = Detector(query).language.name
    if getResourceFromDBPedia(
            queryBeforePreprocessing)["verification"] == False:
        if (
                queryLanguage == "Spanish" or queryLanguage != "English"
        ):  # HACK: AS LONG AS THERE IS ONLY SUPPORT FOR SPANISH-ENGLISH TRANSLATION, KEEP THIS LINE
            query = translate(query)
            queryList = query.split(" ")[:-2]
            if queryList[0] == "the":
                queryList.pop(0)
            del query
            query = " ".join(queryList)
        spellCheckerSuggestions = spellChecker.lookup_compound(
            query, 2)  # LAST PARAMETER INDICATES MAX EDIT DISTANCE LOOKUP
        query = " ".join(
            [suggestion.term for suggestion in spellCheckerSuggestions])
    else:
        query = queryBeforePreprocessing
    query = query.lower()
    try:
        q_vec = getSentenceMeanVector(query)
    except:
        return jsonify(
            result={
                "answer": "No relevant information available.",
                "small_summary": "No relevant information available.",
                "reply": escapeHTMLString(predict_chatbot_response(query)),
                "time": time.time() - start,
                "corrected": query,
                "urls": [],
                "images": [],
                "n_res": 0,
                "map": "",
                "chatbot": 0,
            })

    search = FUTURE.searchIndex(q_vec, 25)
    imageVectorIds, _ = hnswImagesLookup.knn_query(q_vec, k=25)
    numberOfURLs = 25  # LATER ADD SUPORT TO ONLY GET IMPORTANT URLS

    urls = [{
        "url": escapeHTMLString(url["url"]),
        "domain": escapeHTMLString(url["domain"]),
        "header": escapeHTMLString(url["sentence"]),
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

    with imageDBIndex.begin() as imageDBTransaction:
        imagesBinaryDictionary = [
            bson.loads(imageDBTransaction.get(
                str(image).encode("utf-8")))["url"]
            for image in imageVectorIds[0]
        ]  # [:n_imgs]]

    return jsonify(
        result={
            "answer": escapeHTMLString(getAbstractFromDBPedia(query)),
            "small_summary": escapeHTMLString(getDefinitionFromDBPedia(query)),
            "reply": escapeHTMLString(predict_chatbot_response(query)),
            "time": time.time() - start,
            "corrected": escapeHTMLString(query),
            "urls": urls,
            "images": imagesBinaryDictionary,
            "n_res": numberOfURLs,
            "map": getMap(queryBeforePreprocessing, query),
            "chatbot": queryClassifier.test(query),
        })


@app.route("/sourcery", methods=["GET", "POST"])
@login_required
def sourcery():
    name = current_user.get_id()
    iws = IWSearch()
    if iws.validate_on_submit():
        return redirect("/iw/search/user/" + iws.search.data)

    try:
        publications = []
        for x in accounts.find_one({"name": name})["post"]:
            try:
                if x["image"] != "" or x["image"] != None:
                    x["image"] = [[x, mimetypes.guess_type(x)[0]]
                                  for x in x["image"]
                                  if mimetypes.guess_type(x)[0] is not None]
                    publications.append([
                        x["tagged_by"], x["content"], "tagged you in",
                        x["image"]
                    ])
                else:
                    publications.append(
                        [x["tagged_by"], x["content"], "tagged you in"])
            except:
                pass
    except:
        publications = []
    return render_template("sourcery.html",
                           name=name,
                           publications=publications[::-1],
                           iws=iws)


@app.route("/_posts", methods=["GET", "POST"])
@login_required
def get_posts():
    name = current_user.get_id()
    result = []
    try:
        for x in accounts.find_one({"name": name})["follow"]:
            try:
                result.append([
                    escapeHTMLString(x),
                    escapeHTMLString([
                        z for z in [
                            y for y in accounts.find_one({"name": x})["post"]
                            if "tagged_by" not in y
                        ] if name not in z["tagged_list"]
                    ][-1]["content"]),
                    "posted",
                ])
            except:
                pass
    except:
        pass
    return jsonify(result=result)


@app.route("/iw/search/user/<username>", methods=["GET", "POST"])
@login_required
def search_user(username):
    name = current_user.get_id()
    iws = IWSearch()
    if iws.validate_on_submit():
        return redirect("/iw/search/user/" + iws.search.data)
    regx = re.compile("^" + username, re.IGNORECASE)
    names = [
        escapeHTMLString(x["name"]) for x in accounts.find({"name": regx})
        if len(x) <= 10
    ]  # [::-1]
    return render_template("iws.html", iws=iws, names=names)


@app.route("/iw/user/<username>", methods=["GET", "POST"])
@login_required
def see_user(username):
    name = current_user.get_id()
    iws = IWSearch()
    if iws.validate_on_submit():
        return redirect("/iw/search/user/" + iws.search.data)

    try:
        publications = []
        for x in accounts.find_one({"name": username})["post"]:
            if x["image"] != [] or x["image"] != None:
                x["image"] = [[x, mimetypes.guess_type(x)[0]]
                              for x in x["image"]
                              if mimetypes.guess_type(x)[0] is not None]
                try:
                    if username == name:
                        publications.append([
                            escapeHTMLString(x["tagged_by"]),
                            escapeHTMLString(x["content"]), "tagged you in",
                            x["image"]
                        ])
                    else:
                        publications.append([
                            escapeHTMLString(x["tagged_by"]),
                            escapeHTMLString(x["content"]), "tagged him in",
                            x["image"]
                        ])
                except:
                    publications.append([
                        escapeHTMLString(username),
                        escapeHTMLString(x["content"]), "posted", x["image"]
                    ])
            else:
                try:
                    if username == name:
                        publications.append([
                            escapeHTMLString(x["tagged_by"]),
                            escapeHTMLString(x["content"]), "tagged you in"
                        ])
                    else:
                        publications.append([
                            escapeHTMLString(x["tagged_by"]),
                            escapeHTMLString(x["content"]), "tagged him in"
                        ])
                except:
                    publications.append([
                        escapeHTMLString(username),
                        escapeHTMLString(x["content"]), "posted"
                    ])
    except:
        publications = []

    try:
        following = (username in accounts.find_one({"name": name})["follow"])
    except:
        following = False

    return render_template(
        "user.html",
        username=username,
        publications=publications[::-1],
        following=following,
        iws=iws,
    )


@app.route("/follow/<username>", methods=["GET", "POST"])
@login_required
def follow(username):
    accounts.update({"name": current_user.get_id()},
                    {"$push": {
                        "follow": username
                    }},
                    upsert=True)
    return redirect("/iw/user/" + username)


@app.route("/unfollow/<username>", methods=["GET", "POST"])
@login_required
def unfollow(username):
    accounts.update({"name": current_user.get_id()},
                    {"$pull": {
                        "follow": username
                    }},
                    upsert=True)
    return redirect("/iw/user/" + username)


@app.route("/_upload", methods=["GET", "POST"])
@login_required
def _upload():
    name = current_user.get_id()
    try:
        text = request.form["publication"]
    except:
        text = request.form["publication2"]
    for file in request.files.getlist("file"):
        if file:
            file.save(
                os.path.join(dirname, "static/.MAZE/" + name,
                             secure_filename(file.filename)))
    accounts.update(
        {"name": name},
        {
            "$push": {
                "post": {
                    "content":
                    text,
                    "image": [
                        secure_filename(secure_filename(x.filename))
                        for x in request.files.getlist("file")
                    ],
                    "tagged_list":
                    getTaggedNames(text),
                    "date":
                    datetime.datetime.utcnow(),
                }
            }
        },
        upsert=True,
    )
    for tagged in getTaggedNames(text):
        accounts.update(
            {"name": tagged},
            {
                "$push": {
                    "post": {
                        "tagged_by":
                        name,
                        "content":
                        text,
                        "image": [
                            secure_filename(x.filename)
                            for x in request.files.getlist("file")
                        ],
                        "date":
                        datetime.datetime.utcnow(),
                    }
                }
            },
            upsert=True,
        )

    return jsonify(result={"answer": "hi"})


@app.route("/_upload/<username>", methods=["GET", "POST"])
@login_required
def _upload_two(username):
    name = current_user.get_id()
    try:
        text = request.form["publication"]
    except:
        text = request.form["publication2"]
    for file in request.files.getlist("file"):
        if file:
            file.save(
                os.path.join(dirname, "static/.MAZE/" + name,
                             secure_filename(file.filename)))

    accounts.update(
        {"name": name},
        {
            "$push": {
                "post": {
                    "content":
                    text,
                    "image": [
                        secure_filename(x.filename)
                        for x in request.files.getlist("file")
                    ],
                    "tagged_list":
                    appendIfNotInList(username, getTaggedNames(text)),
                    "date":
                    datetime.datetime.utcnow(),
                }
            }
        },
        upsert=True,
    )
    for tagged in appendIfNotInList(username, getTaggedNames(text)):
        accounts.update(
            {"name": tagged},
            {
                "$push": {
                    "post": {
                        "tagged_by":
                        name,
                        "content":
                        text,
                        "image": [
                            secure_filename(x.filename)
                            for x in request.files.getlist("file")
                        ],
                        "date":
                        datetime.datetime.utcnow(),
                    }
                }
            },
            upsert=True,
        )
    return redirect("/iw/user/" + username)


@app.route("/maze", methods=["GET", "POST"])
@login_required
def maze():
    name = current_user.get_id()
    if not os.path.exists(os.path.join(dirname, "static/.MAZE/" + name)):
        os.makedirs(os.path.join(dirname, "static/.MAZE/" + name))
    form = SearchForm()
    if form.validate_on_submit():
        return redirect("/share/" + form.searchbar.data)
    return render_template("maze.html", text=name, form=form)


@app.route("/edit/<filename>", methods=["GET", "POST"])
@login_required
def edit(filename):
    name = current_user.get_id()
    editf = EditForm()
    filem = open(
        os.path.join(dirname, "static/.MAZE/" + name + "/" + filename), "r")
    content = filem.read()
    filem.close()
    if editf.validate_on_submit():
        filen = open(
            os.path.join(dirname, "static/.MAZE/" + name + "/" + filename),
            "w")
        filen.write(editf.code.data)
        filen.close()
        return redirect("/maze")
    return render_template("edit.html",
                           content=content,
                           editf=editf,
                           filey=filename)


@app.route("/MAZE/<filename>")
@login_required
def getFile(filename):
    return send_file(
        os.path.join(dirname,
                     "static/.MAZE/" + current_user.get_id() + "/" + filename),
        as_attachment=True,
    )


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    for file in request.files.getlist("file"):
        if file:
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(dirname, "static/.MAZE/" + current_user.get_id(),
                             filename))
    return redirect("/maze")


@app.route("/_files", methods=["GET", "POST"])
@login_required
def get_files():
    directory = sorted(
        os.listdir(
            os.path.join(dirname, "static/.MAZE/" + current_user.get_id())),
        key=str.lower,
    )
    q = request.args.get("q", "", type=str)
    if q != "":
        result = [s for s in directory if q.lower() in s.lower()]
    else:
        result = directory
    return jsonify(result=[escapeHTMLString(x) for x in result])


@app.route("/remove/<filename>")
@login_required
def remove(filename):
    name = current_user.get_id()
    if os.path.isdir(
            os.path.join(dirname, "static/.MAZE/" + name + "/" + filename)):
        shutil.rmtree(
            os.path.join(dirname, "static/.MAZE/" + name + "/" + filename))
    else:
        os.remove(
            os.path.join(dirname, "static/.MAZE/" + name + "/" + filename))
    return redirect("/maze")


@app.route("/share/<filename>/<recipient>")
@login_required
def share(filename, recipient):
    shutil.copy2(
        os.path.join(dirname,
                     "static/.MAZE/" + current_user.get_id() + "/" + filename),
        os.path.join(dirname, "static/.MAZE/" + recipient + "/" + filename),
    )
    return redirect("/maze")


if __name__ == "__main__":
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host="0.0.0.0", port=int("3000"), debug=True)
