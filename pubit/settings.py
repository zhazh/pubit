# -*- coding: utf-8 -*-
"""
.settings
=================
Configuration.
"""

import os
import sys

_win = sys.platform.startswith("win")
if _win:
    _prefix = "sqlite:///"
else:
    _prefix = "sqlite:////"

_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "2c4dba7087374b5d8a1b91c5dbd46099")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # app defined.
    BRAND = os.getenv("BRAND", "Pubit")

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = _prefix + os.path.join(_basedir, "data-dev.db")

class TestingConfig(BaseConfig):
    WTF_CSRF_ENABLED = False # Default value is True, Close it for testing.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database.

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", _prefix + os.path.join(_basedir, "data.db"))

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}




