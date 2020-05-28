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
from pubit.apis.resps import RespSuccess, RespServerWrong, RespArgumentWrong, RespUnauthenticated
from pubit.apis.v1 import api_v1
from pubit.apis.v1.schemas import pub_schema, node_schema

class IndexAPI(MethodView):
    def get(self):
        return jsonify({
            'version':  '0.0.1',
            'base_url': 'http://pubit.com/api',
            'pub_url':  'http://pubit.com/api/pub',
        })

class PubAPI(MethodView):
    """ Pub item operation provide for admin.
    """
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
                base_dir = current_app.config['ADMIN_HOME']
                node = Node(base_dir=base_dir, path=path)
                location = node.local_path
                if not os.path.isdir(location):
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
        
            if is_public:
                pub = Pubitem(name=name, description=description, location=location, is_public=is_public, allow_upload=allow_upload)
            else:
                pub = Pubitem(name=name, description=description, location=location, password=password, is_public=is_public, allow_upload=allow_upload)
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

class ItemAPI(MethodView):
    def get(self, uuid):
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            if pub is None:
                return RespArgumentWrong('uuid', 'invalid.').jsonify
            if not pub.is_public:
                #protected folder item.
                session_pub = session.get('pub')
                if session_pub is None or session_pub != uuid:
                    return RespUnauthenticated().jsonify
            
            path = request.args.get('path', None)
            if path is None:
                #: Return pub folder root directory tree.
                node = Node(base_dir=pub.location, path='/')
                return jsonify(node.tree)
            else:
                #: Return pub item sub directory(path) file and directory.
                node = Node(base_dir=pub.location, path=path)
                node_list = list()
                for subnode in node.children:
                    node_list.append(node_schema(subnode))
                return jsonify(node_list)
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/pub', view_func=PubAPI.as_view('pub'), methods=['GET', 'POST'])
api_v1.add_url_rule('/pub/<int:pub_id>', view_func=PubAPI.as_view('pub_item'), methods=['GET', 'PUT', 'DELETE'])
api_v1.add_url_rule('/item/<uuid>', view_func=ItemAPI.as_view('item'), methods=['GET'])