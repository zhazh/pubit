# -*- coding: utf-8 -*-
"""
.blueprints.pub
======================
publish folders action.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)
from pubit.forms import PubAuthForm
from pubit.models import Pubitem

pub_bp = Blueprint('pub', __name__)

@pub_bp.route('/', methods=['GET', 'POST'])
def login():
    """ Protectd folder auth.
    """
    form = PubAuthForm()
    if form.validate_on_submit():
        pubname = form.pubname.data
        password = form.password.data
        pub = Pubitem.query.filter(Pubitem.name==pubname).first()
        if pub and pub.password==password:
           return redirect(url_for('pub.item', uuid=pub.uuid)) 
        else:
            form.pubname.errors.append('Invalid pubname or password.')
    return render_template('pub/login.html', form=form)

@pub_bp.route('/<uuid>')
def item(uuid):
    return render_template('pub/item.html', uuid=uuid)


