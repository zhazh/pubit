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

class NewPubitemForm(FlaskForm):
    pubname = StringField('Pub name', validators=[
        DataRequired(message='Pubname required'), 
        Length(1,20, message='Length between 1 and 20')
    ])
    description = TextAreaField('Pub description', validators=[
        Length(0, 512, message='Length more than 512')
    ])

    path = StringField('Pub path', validators=[
        DataRequired(message='Pub path required'), 
    ])

    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm password', validators=[
        EqualTo(password)
    ])

    is_public = BooleanField('is_public', default=True)
    allow_upload = BooleanField('allow_upload', default=False)

    submit = SubmitField('Create')