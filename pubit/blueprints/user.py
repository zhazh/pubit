# -*- coding: utf-8 -*-
"""
.blueprints.user
===================
User manage actions.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request
)
from flask_login import login_user, logout_user, login_required, current_user
from pubit.forms import LoginForm
from pubit.models import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    return redirect(url_for('user.login'))

@user_bp.route('/login', methods=['GET', 'POST'])
def login(): 
    form = LoginForm()
    if form.validate_on_submit():
        if User.check(form.username.data, form.password.data):
            user = User.query.filter(User.name == form.username.data).first()
            login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            return redirect(next or url_for('user.home'))
        else:
            form.username.errors.append("Incorrect username or password")
    return render_template('user/login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user_bp.route('/home')
@login_required
def home():
    return render_template('user/home.html')
