# -*- coding: utf-8 -*-
"""
.apis.decorators
"""
from functools import wraps
from flask import current_app, session, redirect, url_for, jsonify
from .resps import RespUnauthenticated, RespArgumentWrong
from pubit.models import Pubitem

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if session.get('admin') is None:
            return RespUnauthenticated().jsonify
        return func(*args, **kw)
    return wrapper

def node_required(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if 'uuid' not in kw.keys():
            return RespArgumentWrong('uuid', 'missed.').jsonify
        uuid = kw['uuid']
        pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
        if pub is None:
            return RespArgumentWrong('uuid', 'invalid.').jsonify
        if not pub.is_public:
            #protected folder item.
            session_pub = session.get('pub', None)
            if session_pub is None or session_pub != uuid:
                return RespUnauthenticated().jsonify
        return func(*args, **kw)
    return wrapper