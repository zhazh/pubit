# -*- coding: utf-8 -*-
"""
.forms
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField, SelectMultipleField, RadioField, 
                IntegerField, FloatField, FileField, TextAreaField,  DateTimeField, HiddenField, SubmitField)
from wtforms.validators import (ValidationError, 
                DataRequired, InputRequired, NumberRange, Email, EqualTo, Length,
                Regexp, URL, AnyOf, NoneOf)
from sqlalchemy import func, exists, and_, or_
from flask import current_app
import os

class LoginForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message='Username required'), 
        Length(1,20, message='Length between 1 and 20')
    ])
    password = PasswordField('password', validators=[
        DataRequired(message='Password required'), 
        Length(5,20, message='Length between 5 and 20')
    ])
    submit = SubmitField('Sign in')