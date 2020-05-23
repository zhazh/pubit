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

class Pubitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(512))
    created = db.Column(db.DateTime, default=datetime.now)
    path = db.Column(db.String(512))
    password = db.Column(db.String(20), default=None)
    is_valid = db.Column(db.Boolean, default=True)
    allow_upload = db.Column(db.Boolean, default=False)

