# -*- coding: utf-8 -*-
"""
.blueprints.home
======================
web index views.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('index.html')



