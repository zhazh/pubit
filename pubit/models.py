# -*- coding: utf-8 -*-
"""
.models
===========================
Sqlalchemy database models.
"""
import os
from datetime import datetime
from flask import current_app
from uuid import uuid1
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, func, exists, and_, or_
from .extensions import db

class Pubitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(512))
    pubtime = db.Column(db.DateTime, default=datetime.now)
    location = db.Column(db.String(512))
    password = db.Column(db.String(20), default=None)
    is_public = db.Column(db.Boolean, default=True)
    allow_upload = db.Column(db.Boolean, default=False)

    def __init__(self, **kw):
        kw['uuid'] = uuid1().hex
        super().__init__(**kw)
    
    @property
    def standard_pubtime(self):
        return self.pubtime.strftime("%Y/%m/%d %H:%M")
    
    @property
    def access(self):
        return 'public' if self.is_public else 'protected'



