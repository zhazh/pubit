# -*- coding: utf-8 -*-
"""
.blueprints.api.v1
================================
Provide methods for ajax request.
"""
from flask import Blueprint
from flask_cors import CORS

api_v1 = Blueprint('api', __name__)
CORS(api_v1)

from . import resources


