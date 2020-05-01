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

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    searchbar = StringField("searchbar", validators=[DataRequired()])


class MazeAForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    passphrase = PasswordField("passphrase", validators=[DataRequired()])


class MailForm2(FlaskForm):
    mail = StringField("mail", validators=[DataRequired()])


class IWPublish(FlaskForm):
    publication = StringField("publication", validators=[DataRequired()])


class IWSearch(FlaskForm):
    search = StringField("search", validators=[DataRequired()])


class EditForm(FlaskForm):
    code = TextAreaField("code")


class SignForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    confirmPassword = PasswordField("confirmPassword",
                                    validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])


class LoginForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
