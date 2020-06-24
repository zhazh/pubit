# -*- coding: utf-8 -*-
"""
.blueprints.home
======================
web index views.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)
from pubit.models import Pubitem

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    pubs = Pubitem.query.filter(Pubitem.is_public==True).all()
    return render_template('index.html', pubs=pubs)



