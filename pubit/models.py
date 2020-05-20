# -*- coding: utf-8 -*-
"""
.models
===========================
Sqlalchemy database models.
"""
import os
from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, func, exists, and_, or_
from .extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, unique=True)
    hash_passwd = db.Column(db.String(128))
    home = db.Column(db.String(256))
    created = db.Column(db.DateTime, default=datetime.now)
    pubitems = db.relationship('Pubitem', backref='owner', lazy='dynamic')

    def __init__(self, **kw):
        if kw:
            password = kw.pop('password', None)
            if password:
                kw['hash_passwd'] = generate_password_hash(password)
        super(User, self).__init__(**kw)

    # rewrite equal function.
    def __eq__(self, other):
        if type(other) == type(self):
            return self.id == other.id
        return False
    
    # rewrite not equal function.
    def __ne__(self, other):
        return not self.__eq__(other)
    
    # rewrite string function.
    def __repr__(self):
        return 'User[id:%d, name:%s]'%(self.id, self.name)
    
    @classmethod
    def check(cls, name, password):
        """ Check login by username and password
            :returns: boolean.
        """
        usr = cls.query.filter_by(name=name).first()
        if usr:
            return check_password_hash(usr.hash_passwd, password)
        return False

    def equal_password(self, password):
        return check_password_hash(self.hash_passwd, password)

    def set_password(self, password):
        self.hash_passwd = generate_password_hash(password)

    def set_home(self, home):
        try:
            self.home = home
            if not os.path.exists(self.home):
                os.makedirs(self.home)
        except:
            raise ValueError("Argument 'home':%s cann't access."%home)

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

class Pubitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(512))
    created = db.Column(db.DateTime, default=datetime.now)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(512))
    share_code = db.Column(db.String(20), default=None)
    is_valid = db.Column(db.Boolean, default=True)

