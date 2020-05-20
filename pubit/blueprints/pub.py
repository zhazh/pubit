# -*- coding: utf-8 -*-
"""
.blueprints.pub
======================
public resource views.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)

pub_bp = Blueprint('pub', __name__)

@pub_bp.route('/')
def index():
    return 'Index of Pubs.'


