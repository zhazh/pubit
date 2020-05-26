# -*- coding: utf-8 -*-
"""
pubit.
====================================
Provide factory function `create_app`.
"""

import os
import click
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from .settings import config
from .extensions import (db, login_manager, migrate, csrf)
from .blueprints import home_bp, admin_bp, pub_bp
from .apis import api_bp

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "production")
    app = Flask("pubit")
    app.config.from_object(config[config_name])

    register_logger(app)
    register_extensions(app)
    register_template_context(app)
    register_errors(app)
    register_blueprints(app)
    register_commands(app)
    return app

def register_logger(app):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/app.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    if not app.debug:
        app.logger.addHandler(file_handler)

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        return dict(BRAND=app.config['BRAND'])

def register_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning('404 - path: %s'%request.full_path)
        return render_template('errors/error.html', error=e), 404
    
    @app.errorhandler(CSRFError)
    def handler_csrf_error(e):
        # handle csrf protect error.
        app.logger.warning('400 - path: %s, description:%s'%(request.full_path, e.description))
        return render_template('errors/error.html', error=e), 400
    
def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(pub_bp, url_prefix='/pub')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    #app.register_blueprint(api_bp, url_prefix='/api', subdomain='api')  # enable subdomain support

def register_commands(app):
    @app.cli.command()
    def init():
        """ Initialize database and default user """
        db.create_all()
        click.echo("Initialized database.")
        click.echo("Done.")
