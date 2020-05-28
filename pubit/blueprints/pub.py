# -*- coding: utf-8 -*-
"""
.blueprints.pub
======================
publish folders action.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, 
    request, session, abort
)
from pubit.forms import PubAuthForm
from pubit.models import Pubitem

pub_bp = Blueprint('pub', __name__)

@pub_bp.route('/', methods=['GET', 'POST'])
def login():
    """ Protectd folder auth.
    """
    if session.get('pub'):
        return redirect(url_for('pub.item', uuid=session.get('pub')))

    form = PubAuthForm()
    if form.validate_on_submit():
        pubname = form.pubname.data
        password = form.password.data
        pub = Pubitem.query.filter(Pubitem.name==pubname).first()
        if pub and pub.password==password:
            session['pub'] = pub.uuid
            return redirect(url_for('pub.item', uuid=pub.uuid)) 
        else:
            form.pubname.errors.append('Invalid pubname or password.')
    return render_template('pub/login.html', form=form)

@pub_bp.route('/logout')
def logout():
    if session.get('pub'):
        session.pop('pub')
    return redirect(url_for('pub.login'))

@pub_bp.route('/<uuid>')
def item(uuid):
    pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
    if pub is None:
        abort(404)
    if not pub.is_public:
        # protected.
        session_pub = session.get('pub', None)
        if session_pub is None or session_pub != uuid:
            return redirect(url_for('pub.login'))
    return render_template('pub/item.html', pub=pub)
