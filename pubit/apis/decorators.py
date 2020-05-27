# -*- coding: utf-8 -*-
"""
.apis.decorators
"""
from functools import wraps
from flask import current_app, session, redirect, url_for, jsonify
from .resps import RespUnauthenticated

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if session.get('admin') is None:
            return RespUnauthenticated().jsonify
        return func(*args, **kw)
    return wrapper