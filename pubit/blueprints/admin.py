# -*- coding: utf-8 -*-
"""
.blueprints.user
===================
User manage actions.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request, 
    current_app, session
)
from pubit.forms import LoginForm, NewPubitemForm
from pubit.decorators import admin_check, admin_authed, admin_login, admin_logout, admin_required
from pubit.models import Pubitem

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
    pubs = Pubitem.query.all()
    return render_template('admin/home.html', pubs=pubs)

@admin_bp.route('/create')
@admin_required
def create():
    form = NewPubitemForm()
    if form.validate_on_submit():
        pass
    return render_template('admin/new.html', form=form)
