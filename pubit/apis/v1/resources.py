# -*- coding: utf-8 -*-
"""
.apis.v1.resources
================================
Provide resources for ajax request.
"""
import os
from flask.views import MethodView
from flask import (
    render_template, redirect, url_for, request, current_app,
    session, jsonify, send_from_directory, make_response
)
from sqlalchemy.exc import IntegrityError
from pubit.decorators import admin_check, admin_authed, admin_login, admin_logout, admin_required
from pubit.models import Pubitem
from pubit.node import NodePath, NodeFactory, Node, DirectoryNode
from pubit.extensions import db
from pubit.service import Service
from pubit.apis.decorators import admin_required, node_required
from pubit.apis.resps import RespSuccess, RespServerWrong, RespArgumentWrong, RespUnauthenticated
from pubit.apis.v1 import api_v1
from pubit.apis.v1.schemas import pub_schema, node_schema

class IndexAPI(MethodView):
    """ Api rescources list.
        pubs_url:           switch (request method):
                                    case `get`:  return all pubs.
                                    case `post`: create an pub.
        pub_url:            switch (request method):
                                    case `get`:  return a single pub.
                                    case `put`:  modify an pub.
                                    case `delete`:  delete an pub. 
        node_url:           switch (request method):
                                    case `get`:  return the pub node description, if node is directory also return children
                                    case `post`: create an subnode in the pub node.
                                    case `put`:  modify an pub node.
                                    case `delete`:  delete an pub node.
        node_dir_url:       switch(request method):
                                    case `get`: return directories of the pub node.
        node_search_url:    switch(request method):
                                    case `get`: return the search result of keywords in the pub node.
        node_load_url:      switch (request methid):
                                    case `get`:     download the pub node.
                                    case `post`:    upload file or folder to the pub node.
    """
    base_url = 'http://api.pubit.com'

    def get(self):
        return jsonify({
            'version':          '0.0.1',
            'base_url':         '%s'%self.__class__.base_url,
            'pubs_url':         '%s/pub'%self.__class__.base_url,      
            'pub_url':          '%s/pub/<uuid>'%self.__class__.base_url,      
            'node_url':         '%s/pub/<uuid>/<node_id>'%self.__class__.base_url,
            'node_dir_url':     '%s/pub/<uuid>/<node_id>/dir'%self.__class__.base_url,
            'node_search_url':  '%s/pub/<uuid>/<node_id>/search'%self.__class__.base_url,
            'node_upload_url':  '%s/pub/<uuid>/<node_id>/upload'%self.__class__.base_url,
        })

class PubAPI(MethodView):
    """ Publish folder(Pub) operation api.
    """
    decorators = [admin_required]

    def get(self, uuid=None):
        """ Return pub item description.
            :param uuid: if set to `None` return all pubs list,
                         otherwise return a single pub.
        """
        try:
            if uuid is None:
                # return all pub items.
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
            base_dir = current_app.config['ADMIN_HOME']
            node = NodeFactory.create(key=path, base_dir=base_dir)
            if not isinstance(node, DirectoryNode):
                return RespArgumentWrong('path', 'invalid').jsonify
            location = node.local_path

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
            import traceback
            traceback.print_exc()
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

class NodeAPI(MethodView):
    decorators = [node_required]

    def get(self, uuid, node_id):
        """ Return an node description.
            if node is directory will return children in `children` section.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            node = pub.node(node_id)
            return jsonify(node_schema(node))
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def post(self, uuid, node_id):
        """ Create new folder in this node.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            node = pub.node(node_id)
            if not isinstance(node, DirectoryNode):
                return RespArgumentWrong('Node', 'is not an directory').jsonify

            name = request.form.get('name', None)
            if name is None:
                return RespArgumentWrong('name', 'missed').jsonify
            
            local_path = os.path.join(node.local_path, name)
            Service().send('new', target=local_path)
            return RespSuccess().jsonify
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except FileExistsError as e:
            current_app.logger.error(e)
            return RespServerWrong('The folder already exists').jsonify
        except PermissionError as e:
            current_app.logger.error(e)
            return RespServerWrong('Permission denied').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify
    
    def put(self, uuid, node_id):
        """ Modify the node's name.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            node = pub.node(node_id)
            old_name = request.form.get('old_name', None)
            if old_name is None:
                return RespArgumentWrong('old_name', 'missed').jsonify

            new_name = request.form.get('new_name', None)
            if new_name is None:
                return RespArgumentWrong('new_name', 'missed').jsonify

            old_local_path = os.path.join(node.local_path, old_name)
            new_local_path = os.path.join(node.local_path, new_name)
            if os.path.exists(new_local_path):
                raise FileExistsError(new_local_path)
            Service().send('move', src=old_local_path, dst=new_local_path)
            return RespSuccess().jsonify
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except FileExistsError as e:
            current_app.logger.error(e)
            return RespServerWrong('The node already exists').jsonify
        except PermissionError as e:
            current_app.logger.error(e)
            return RespServerWrong('Permission denied').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

    def delete(self, uuid, node_id):
        """ Delete an node(folder or file).
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()            
            node = pub.node(node_id)
            Service().send('delete', target=node.local_path)
            return RespSuccess().jsonify
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

class NodeDirAPI(MethodView):
    decorators = [node_required]
    def get(self, uuid, node_id):
        """ Return node children dirctories for jstree.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            node = pub.node(node_id)
            if not isinstance(node, DirectoryNode):
                return RespArgumentWrong('Node', 'is not an directory').jsonify
            if node_id == '|':
                node_desc = dict(id=node.id, text=node.name, state=dict(opened=True, selected=True), data=dict(path=node.path), children=True)
            else:
                node_desc = dict(id=node.id, text=node.name, state=dict(opened=True), data=dict(path=node.path), children=True)
            children_dir = list()
            for subnode in node.children():
                if isinstance(subnode, DirectoryNode):
                    children_dir.append(dict(id=subnode.id, text=subnode.name, data=dict(path=subnode.path), children=True))
            node_desc['children'] = children_dir
            return jsonify(node_desc)
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

class NodeSearchAPI(MethodView):
    decorators = [node_required]
    def get(self, uuid, node_id):
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            keywords = request.args.get('keywords', None)
            if keywords is None:
                return RespArgumentWrong('keywords', 'missed.').jsonify
            node = pub.node(node_id)
            if not isinstance(node, DirectoryNode):
                return RespArgumentWrong('Node', 'is not an directory').jsonify
            node_list = list()
            for nd in node.search(keywords):
                node_list.append(node_schema(nd))
            return jsonify(node_list)
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify

class NodeUploadAPI(MethodView):
    decorators = [node_required]
    def post(self, uuid, node_id):
        """ Node(File/Directory) upload.
        """
        try:
            pub = Pubitem.query.filter(Pubitem.uuid==uuid).first()
            node = pub.node(node_id)
            if not isinstance(node, DirectoryNode):
                return RespArgumentWrong('Node', 'is not an directory').jsonify
            f = request.files['file']
            basedir = node.local_path
            local_path = os.path.join(basedir, f.filename)
            f.save(local_path)
            return RespSuccess().jsonify
        except TypeError as e:
            current_app.logger.error(e)
            return RespArgumentWrong('Node', 'is not a valid node').jsonify
        except Exception as e:
            current_app.logger.error(e)
            return RespServerWrong().jsonify
    
api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/pub', view_func=PubAPI.as_view('pubs'), methods=['GET', 'POST'])
api_v1.add_url_rule('/pub/<uuid>', view_func=PubAPI.as_view('pub'), methods=['GET', 'PUT', 'DELETE'])
api_v1.add_url_rule('/pub/<uuid>/<node_id>', view_func=NodeAPI.as_view('node'), methods=['GET', 'POST', 'PUT', 'DELETE'])
api_v1.add_url_rule('/pub/<uuid>/<node_id>/dir', view_func=NodeDirAPI.as_view('node_dir'), methods=['GET'])
api_v1.add_url_rule('/pub/<uuid>/<node_id>/search', view_func=NodeSearchAPI.as_view('node_search'), methods=['GET'])
api_v1.add_url_rule('/pub/<uuid>/<node_id>/upload', view_func=NodeUploadAPI.as_view('node_upload'), methods=['POST'])
