# -*- coding: utf-8 -*-
"""
.blueprints.user
===================
User manage actions.
"""
import os
from flask import (
    Blueprint, render_template, redirect, url_for, request, 
    current_app, session, jsonify
)
from sqlalchemy.exc import IntegrityError
from pubit.forms import LoginForm, NewPubitemForm
from pubit.decorators import admin_check, admin_authed, admin_login, admin_logout, admin_required
from pubit.models import Pubitem
from pubit.service import Node
from pubit.extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET', 'POST'])
def login(): 
    if admin_authed():
        return redirect(url_for('admin.home'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if admin_check(username, password):
            admin_login(username)
            return redirect(url_for('admin.home'))
        else:
            form.username.errors.append('Incorrect username or password.')
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
@admin_required
def logout():
    admin_logout()
    return redirect(url_for('admin.login'))

@admin_bp.route('/home')
@admin_required
def home():
    pubs = Pubitem.query.order_by(Pubitem.pubtime.desc()).all()
    return render_template('admin/home.html', pubs=pubs)

@admin_bp.route('/dir_tree', methods=['GET'])
def dir_tree():
    """ Response admin home directory list with json data.
    """
    try:
        if not admin_authed():
            # 403 forbidden.
            return jsonify(dict(code=1, msg='Unauthenticated')), 403
        path = request.args.get('path', '/')
        node = Node(path=path)
        return jsonify(node.tree)
    except Exception as e:
        current_app.logger.error('dir_tree:%s'%str(e))
        return jsonify(dict(code=2, msg='Catch an exception')), 500
