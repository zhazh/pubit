# -*- coding: utf-8 -*-
"""
.apis.v1.resources
================================
Provide resources for ajax request.
"""
import os
from flask.views import MethodView
from flask import (
    render_template, redirect, url_for, 
    request, current_app, session, jsonify
)
from sqlalchemy.exc import IntegrityError
from pubit.decorators import admin_check, admin_authed, admin_login, admin_logout, admin_required
from pubit.models import Pubitem
from pubit.service import Node
from pubit.extensions import db
from pubit.apis.decorators import admin_required
from pubit.apis.v1 import api_v1
from pubit.apis.v1.schemas import pub_schema
from pubit.apis.v1.errors import ServerError

class IndexAPI(MethodView):
    def get(self):
        return jsonify({
            'version':  '0.0.1',
            'base_url': 'http://pubit.com/api',
            'pub_url':  'http://pubit.com/api/pub',
        })

class PubAPI(MethodView):
    decorators = [admin_required]

    def get(self):
        """ Return pub item description.
        """
        try:
            pub_id = request.args.get('pub_id', None)
            if pub_id is None:
                # return pub items.
                pubs = list()
                for pub in Pubitem.query.order_by(Pubitem.pubtime.desc()).all():
                    pubs.append(pub_schema(pub))
                return jsonify(pubs)
            else:
                # return single pub item.
                pub = Pubitem.query.get(int(pub_id))
                if pub:
                    return jsonify(pub_schema(pub))
                return jsonify(dict())
        except Exception as e:
            current_app.logger.error(e)
            return ServerError.json_resp

    def post(self):
        """ Create an new pub item.
        """
        pass

    def put(self, pub_id):
        """ Modify an pub item.
        """
        pass

    def delete(self, pub_id):
        """ Delete an pub item.
        """
        pass

api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/pub', view_func=PubAPI.as_view('pub'), methods=['GET', 'POST', 'PUT', 'DELETE'])