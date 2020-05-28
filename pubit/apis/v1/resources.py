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
from pubit.apis.resps import RespSuccess, RespServerWrong, RespArgumentWrong
from pubit.apis.v1 import api_v1
from pubit.apis.v1.schemas import pub_schema

class IndexAPI(MethodView):
    def get(self):
        return jsonify({
            'version':  '0.0.1',
            'base_url': 'http://pubit.com/api',
            'pub_url':  'http://pubit.com/api/pub',
        })

class PubAPI(MethodView):
    decorators = [admin_required]

    def get(self, pub_id=None):
        """ Return pub item description.
        """
        try:
            #pub_id = request.args.get('pub_id', None)
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
                return RespArgumentWrong('pub_id').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def post(self):
        """ Create an new pub item.
        """
        try:
            name = request.form.get('name')
            if name is None:
                return RespArgumentWrong('name', 'missed').jsonify
            description = request.form.get("description", "")
            path = request.form.get("path")
            if path is None:
                return RespArgumentWrong('path', 'missed').jsonify
            else:
                node = Node(path=path)
                if not os.path.isdir(node.local_path):
                    return RespArgumentWrong('path', 'invalid').jsonify

            access = request.form.get("access", "public")
            if access == 'public':
                is_public = True
            else:
                is_public = False
                password = request.form.get("password") 
                if password is None:
                    return RespArgumentWrong('password', 'missed').jsonify
                if len(password) < 5 or len(password) > 20:
                    return RespArgumentWrong('password', 'length must be 5 and 20').jsonify

            allow_upload = request.form.get("allow_upload", "no")
            if allow_upload == 'yes':
                allow_upload = True
            else:
                allow_upload = False

            base_dir = current_app.config['ADMIN_HOME']
            if is_public:
                pub = Pubitem(name=name, description=description, base_dir=base_dir, path=path, is_public=is_public, allow_upload=allow_upload)
            else:
                pub = Pubitem(name=name, description=description, base_dir=base_dir, path=path, password=password, is_public=is_public, allow_upload=allow_upload)
            db.session.add(pub)
            db.session.commit()
            return RespSuccess().jsonify
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(e)
            return RespArgumentWrong('name', 'has existed.').jsonify
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def put(self, pub_id):
        """ Modify an pub item.
        """
        try:
            pub_id = request.form.get('id', None)
            if pub_id is None:
                return RespArgumentWrong('id', 'missed').jsonify
            pub = Pubitem.query.get(int(pub_id))
            if pub is None:
                return RespArgumentWrong('id', 'not existed').jsonify
            
            pub_name = request.form.get('name', None)
            if pub_name is None:
                return RespArgumentWrong('name', 'missed').jsonify
            if len(pub_name) > 20:
                return RespArgumentWrong('name', 'length must less than 20').jsonify

            allow_upload = request.form.get("allow_upload", "yes" if pub.allow_upload else "no")
            if allow_upload == 'yes':
                allow_upload = True
            else:
                allow_upload = False

            if request.form.get('access') == 'public':
                pub.is_public = True
                pub.password = None
            else:
                password = request.form.get('password')
                if password is None:
                    return RespArgumentWrong('password', 'missed').jsonify
                if len(password) < 5 or len(password) > 20:
                    return RespArgumentWrong('password', 'length must be 5 and 20').jsonify
                
                pub.is_public = False
                pub.password = password
            pub.name = pub_name
            pub.description = request.form.get('description', '')
            pub.allow_upload = allow_upload
            db.session.commit()
            return RespSuccess().jsonify
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(e)
            return RespArgumentWrong('name', 'has existed.').jsonify
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def delete(self, pub_id):
        """ Delete an pub item.
        """
        try:
            pub = Pubitem.query.get(int(pub_id))
            if pub:
                db.session.delete(pub)
                db.session.commit()
                return RespSuccess().jsonify
            return RespArgumentWrong('pub_id').jsonify
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return RespServerWrong().jsonify

api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/pub', view_func=PubAPI.as_view('pub'), methods=['GET', 'POST'])
api_v1.add_url_rule('/pub/<int:pub_id>', view_func=PubAPI.as_view('pub_item'), methods=['GET', 'PUT', 'DELETE'])