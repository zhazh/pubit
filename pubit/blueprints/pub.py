# -*- coding: utf-8 -*-
"""
.blueprints.pub
======================
publish folders action.
"""
import os
from flask import (
    Blueprint, render_template, redirect, url_for, current_app,
    request, session, abort, send_from_directory, make_response
)
from pubit.forms import PubAuthForm
from pubit.models import Pubitem, Node

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

@pub_bp.route('/download/<uuid>')
def download(uuid):
    pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
    path = request.args.get('path', None)
    if pub is None or path is None:
        abort(404)
    if not pub.is_public:
        # protected.
        session_pub = session.get('pub', None)
        if session_pub is None or session_pub != uuid:
            return redirect(url_for('pub.login'))
    try:
        node = Node(base_dir=pub.location, path=path)
        if not os.path.isfile(node.local_path):
            raise TypeError("path:'%s' not an file"%path)
        _path, _filename = os.path.split(node.local_path)
        current_app.logger.info("download file: '%s'"%node.local_path)
        response = make_response(send_from_directory(_path, filename=_filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(_filename.encode().decode('latin-1'))
        return response
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
