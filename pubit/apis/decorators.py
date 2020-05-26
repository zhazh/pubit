# -*- coding: utf-8 -*-
"""
.apis.decorators
"""
from functools import wraps
from flask import current_app, session, redirect, url_for, jsonify

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if session.get('admin') is None:
            return jsonify(dict(code=1, msg='Unauthenticated')), 403
        return func(*args, **kw)
    return wrapper