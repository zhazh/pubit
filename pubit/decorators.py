# -*- coding: utf-8 -*-
"""
.decorators
"""
from functools import wraps
from flask import current_app, session, redirect, url_for

def admin_check(name, password):
    admin_name = current_app.config.get('ADMIN_NAME')
    admin_password = current_app.config.get('ADMIN_PASSWORD')
    if name == admin_name and password == admin_password:
        return True
    return False

def admin_authed():
    if session.get('admin') is None:
        return False
    return True

def admin_login(admin_name):
    session['admin'] = admin_name

def admin_logout():
    session.pop('admin')

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if session.get('admin') is None:
            return redirect(url_for('admin.login'))
        return func(*args, **kw)
    return wrapper