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
from pubit.forms import LoginForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET', 'POST'])
def login(): 
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == current_app.config.get('ADMIN_NAME') and password == current_app.config.get('ADMIN_PASSWORD'):
            session['admin'] = username
            return redirect(url_for('admin.home'))
        else:
            form.username.errors.append('Incorrect username or password.')
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    session.pop('admin')
    return redirect(url_for('admin.login'))

@admin_bp.route('/home')
def home():
    if session.get('admin') is None:
        return redirect(url_for('admin.login'))
    return render_template('admin/home.html')
