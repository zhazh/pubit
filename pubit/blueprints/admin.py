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

@admin_bp.route('/new_pub', methods=['POST'])
def new_pub():
    """ Response create new pubitem with json data.
    """
    try:
        if not admin_authed():
            # 403 forbidden.
            return jsonify(dict(code=1, msg='Unauthenticated')), 403
        name = request.form.get('name')
        if name is None:
            return jsonify(dict(code=100, msg="Empty argument 'name'"))
        description = request.form.get("description", "")
        path = request.form.get("path")
        if path is None:
            return jsonify(dict(code=101, msg="Empty argument 'path'"))
        else:
            node = Node(path=path)
            if not os.path.isdir(node.local_path):
                return jsonify(dict(code=102, msg="Invalid argument 'path'"))

        access = request.form.get("access")
        if access == 'public':
            is_public = True
        else:
            is_public = False
            password = request.form.get("password") 
            if password is None:
                return jsonify(dict(code=103, msg="Required argument 'password' and 'confirm_password'."))
            if len(password) < 5 or len(password) > 20:
                return jsonify(dict(code=104, msg="Argument 'password' length must between 5 and 20."))

        allow_upload = request.form.get("allow_upload", "no")
        if allow_upload == 'yes':
            allow_upload = True
        else:
            allow_upload = False

        base_dir = current_app.config['ADMIN_HOME']
        if is_public:
            pub = Pubitem(name=name, description=description, base_dir=base_dir, path=path, is_public=is_public, allow_upload=allow_upload)
        else:
            pub = Pubitem(name=name, description=description, base_dir=base_dir, path=path, password=password, is_public=is_public, allow_upload=allow_upload)
        db.session.add(pub)
        db.session.commit()
        return jsonify(dict(code=0, msg='Success'))
    except IntegrityError as e:     # unique error.
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(dict(code=2, msg="Argument 'name' has existed.")), 500
    except Exception as e:
        current_app.logger.error('new_pub:%s'%str(e))
        db.session.rollback()
        return jsonify(dict(code=2, msg='Catch an exception')), 500