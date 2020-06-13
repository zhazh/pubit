#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import current_app
from .utils import unit_size, standard_timestr, is_binary_file

class NodePath(object):
    @staticmethod
    def correct_the_path(path):
        """ Regularize input path parameters.
        """
        path_list = path.split('/')
        stack = list()
        for p in path_list:
            if p != '':
                if p == '..':
                    if len(stack) > 0:
                        stack.pop()
                else:
                    stack.append(p)
        if len(stack) == 0:
            path = '/'
        else:
            path = ''
            for p in stack:
                path = path + '/' + p
        return path

    @staticmethod
    def path_to_local(base_dir, path):
        """ transform path to local path.
            :arg base_dir: absolute local path of base directory(server-side).
            :arg path: web path style relactive to base_dir.
        """
        path = NodePath.correct_the_path(path)
        valid_path = list(filter(lambda p: p!='', path.split('/')))
        return os.path.join(base_dir, *valid_path)


class Node(object):
    """ Node model, a folder or a file can be a Node.
        Node base attributes:
        :attr id:           node id, a string.
        :attr name:         node name, a string.
        :attr base_dir:     absolute local path of base directory.
        :attr path:         node relative path use linux-style to 'base_dir', such as '/', '/home', '/home/data'.
        :attr parent_id:    parent node id, relative path, if node path is '/', parent_id will set to be `None`.
        :attr local_path:   node local path.
        :attr type:         node type name.
        Node extra attributes:
        :attr size:         node size.
        :attr create:       node create time.
        :attr visit:        node last visit time.
        :attr modify:       node last modify time.
    """
    def __init__(self, key, base_dir=None):
        """ :param key: path or id.
        """
        path = key if key.startswith('/') else key.replace('|', '/')
        self._set_base(path, base_dir)
        self._set_extra()

    def _set_base(self, path, base_dir):
        """ Set base attributes.
        """
        self.base_dir = os.path.normpath(base_dir if base_dir else current_app.config['ADMIN_HOME'])
        if not os.path.isdir(self.base_dir):
            raise TypeError("base_dir:'%s' is not an valid directory."%self.base_dir)
        
        self.path = NodePath.correct_the_path(path)
        if self.path == '/':
            self.name = 'Home'          # root path name is 'Home'
            self.parent_path = None
            self.parent_id = None       # root path parent id is None.
        else:
            self.parent_path, self.name = os.path.split(self.path)
            self.parent_id = self.parent_path.replace('/', '|')
        self.local_path = NodePath.path_to_local(self.base_dir, self.path)
        if not os.path.exists(self.local_path):
            raise TypeError("path:'%s' doesn't exist."%path)

    def _set_extra(self):
        """ Set extra attributes required attr `local_path`.
        """
        node_info = os.stat(self.local_path)
        self.size = unit_size(node_info.st_size)
        self.create = standard_timestr(node_info.st_ctime)
        self.visit = standard_timestr(node_info.st_atime)
        self.modify = standard_timestr(node_info.st_mtime)

    @property
    def type(self):
        return 'Node'

    @property
    def id(self):
        return self.path.replace('/', '|')

    def is_type(self, node_type_class):
        return isinstance(self, node_type_class)

class DirectoryNode(Node):
    def __init__(self, key, base_dir=None):
        super().__init__(key, base_dir)
        if not os.path.isdir(self.local_path):
            raise TypeError('Node is not an directory')

    @property
    def type(self):
        return 'Directory'
    
    def children(self):
        """ Return child node list.
        """
        child_list = list()
        for _name in os.listdir(self.local_path):
            if self.path == '/':
                path = '/' + _name
            else:
                path = self.path + '/' + _name
            node = NodeFactory.create(key=path, base_dir=self.base_dir)
            child_list.append(node)
        return child_list

    def search(self, keywords):
        """ Search keywords in this node, return matched nodes list.
        """
        node_list = list()
        _keywords = list(filter(lambda s:len(s)>0, keywords.split()))
        for root, dirs, files in os.walk(self.local_path):
            for fname in files:
                for keyword in _keywords:
                    if fname.find(keyword) != -1:
                        f_local_path = os.path.join(root, fname)
                        path = f_local_path[len(self.base_dir):].replace(os.path.sep, '/')
                        if path == '':
                            path = '/'
                        node = NodeFactory.create(key=path, base_dir=self.base_dir)
                        node_list.append(node)
        return node_list

class FileNode(Node):
    def __init__(self, key, base_dir=None):
        super().__init__(key, base_dir)
        if not os.path.isfile(self.local_path):
            raise TypeError('Node not an File')
        self.suffix = self.name.split('.')[-1].lower()

    @property
    def type(self):
        try:
            if self.suffix in ('mp3', 'wav'):
                return 'Audio File'
            elif self.suffix in ('mp4', 'mov'):
                return 'Video File'
            elif self.suffix in ('jpg', 'bmp', 'gif', 'png'):
                return 'Photo'
            else:
                if is_binary_file(self.local_path):
                    return 'Binaray File'
                else:
                    return 'Text File'
        except Exception as e:
            return 'No Permission File'

class NodeFactory(object):
    @classmethod
    def create(cls, key, base_dir=None):
        path = key if key.startswith('/') else key.replace('|', '/')
        local_path = NodePath.path_to_local(base_dir, path)
        if os.path.isdir(local_path):
            return DirectoryNode(key, base_dir)
        else:
            return FileNode(key, base_dir)