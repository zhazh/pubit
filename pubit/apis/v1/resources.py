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
from pubit.models import Pubitem, Node
from pubit.extensions import db
from pubit.service import Service
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

    def get(self, uuid=None):
        """ Return pub item description.
        """
        try:
            #pub_id = request.args.get('pub_id', None)
            if uuid is None:
                # return pub items.
                pubs = list()
                for pub in Pubitem.query.order_by(Pubitem.pubtime.desc()).all():
                    pubs.append(pub_schema(pub))
                return jsonify(pubs)
            else:
                # return single pub item.
                pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
                if pub:
                    return jsonify(pub_schema(pub))
                return RespArgumentWrong('uuid').jsonify
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

    def put(self, uuid):
        """ Modify an pub item.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            if pub is None:
                return RespArgumentWrong('uuid', 'not existed').jsonify
            
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

    def delete(self, uuid):
        """ Delete an pub item.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            if pub:
                db.session.delete(pub)
                db.session.commit()
                return RespSuccess().jsonify
            return RespArgumentWrong('uuid').jsonify
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return RespServerWrong().jsonify

class NodesAPI(MethodView):
    def get(self, uuid):
        """ List pub child nodes or root directory tree.
            if request arg `path` is None, return root directory tree.
            else return `path` directory children node.
        """
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

class NodeAPI(MethodView):
    def get(self, uuid):
        """ Return node description.
        """
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
                return RespArgumentWrong('path', 'missed')
            else:
                node = Node(base_dir=pub.location, path=path)
                return jsonify(node_schema(node))
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def post(self, uuid):
        """ Create new folder node.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            if pub is None:
                return RespArgumentWrong('uuid', 'invalid.').jsonify
            if not pub.is_public:
                #protected folder item.
                session_pub = session.get('pub')
                if session_pub is None or session_pub != uuid:
                    return RespUnauthenticated().jsonify
            
            parent_path = request.form.get('parent_path', None)
            if parent_path is None:
                return RespArgumentWrong('parent_path', 'missed').jsonify
            name = request.form.get('name', None)
            if name is None:
                return RespArgumentWrong('name', 'missed').jsonify
            path = parent_path + '/' + name
            folder_path = Node.pathToLocal(pub.location, path)
            Service().send('new', target=folder_path)
            return RespSuccess().jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify
    
    def put(self, uuid):
        """ Modify an node name.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            if pub is None:
                return RespArgumentWrong('uuid', 'invalid.').jsonify
            if not pub.is_public:
                #protected folder item.
                session_pub = session.get('pub')
                if session_pub is None or session_pub != uuid:
                    return RespUnauthenticated().jsonify
            
            path = request.form.get('path', None)
            if path is None:
                return RespArgumentWrong('path', 'missed').jsonify

            name = request.form.get('name', None)
            if name is None:
                return RespArgumentWrong('name', 'missed').jsonify

            node = Node(base_dir=pub.location, path=path)
            _dir, _name = os.path.split(node.local_path)
            Service().send('move', src=node.local_path, dst=os.path.join(_dir, name))
            return RespSuccess().jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def delete(self, uuid):
        """ Delete an node(folder/path)
        """
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
                return RespArgumentWrong('path', 'missed')
            else:
                #: Return pub item sub directory(path) file and directory.
                node = Node(base_dir=pub.location, path=path)
                Service().send('delete', target=node.local_path)
                return RespSuccess().jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify


class SearchAPI(MethodView):
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

            keywords = request.form.get('keywords', None)
            if keywords is None:
                return RespArgumentWrong('keywords', 'missed.')
            node = Node(base_dir=pub.location, path='/')
            node_list = list()
            for nd in node.search(keywords):
                node_list.append(node_schema(nd))
            return jsonify(node_list)
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/pub', view_func=PubAPI.as_view('pub'), methods=['GET', 'POST'])
api_v1.add_url_rule('/pub/<uuid>', view_func=PubAPI.as_view('pub_item'), methods=['GET', 'PUT', 'DELETE'])
api_v1.add_url_rule('/pub/<uuid>/nodes', view_func=NodesAPI.as_view('nodes'), methods=['GET'])
api_v1.add_url_rule('/pub/<uuid>/node', view_func=NodeAPI.as_view('node'), methods=['GET', 'POST', 'PUT', 'DELETE'])
api_v1.add_url_rule('/pub/<uuid>/search', view_func=SearchAPI.as_view('search'), methods=['GET'])