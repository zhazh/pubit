# -*- coding: utf-8 -*-
"""
.blueprints.user
===================
User manage actions.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    return redirect(url_for('user.login'))

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('user/login.html')

@user_bp.route('/home')
def home():
    return render_template('user/home.html')
