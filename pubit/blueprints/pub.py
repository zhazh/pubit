# -*- coding: utf-8 -*-
"""
.blueprints.pub
======================
public resource views.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)
from pubit.forms import PubAuthForm

pub_bp = Blueprint('pub', __name__)

@pub_bp.route('/')
def login():
    form = PubAuthForm()
    if form.validate_on_submit():
        return 'OK'
    return render_template('pub/login.html', form=form)

@pub_bp.route('/<uuid>')
def pub(uuid):
    return 'Pub %s'%uuid


