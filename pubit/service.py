# -*- coding: utf-8 -*-
"""
.service
=================
App middle service.
"""
import os
import time
from datetime import datetime
from flask import current_app

def _kb_size(size):
    return '%.2f Kb' %(size/1024)

def _standard_timestr(localtime):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(localtime))

class Node(object):
    def __init__(self, base_dir=None, path=None):
        """ Initialize node object with attributes.
            `path`: web path such as '/', '/home', '/home/data'
            `name`: node name root path name is 'Home'
            `local_path`: the full path of node in server.
        """
        if base_dir is None:
            self.base_dir = current_app.config.get('ADMIN_HOME')
        else:
            self.base_dir = base_dir
        self.path = self._rectify(path)
        if self.path == '/':
            self._set_base_use_default()
        else:
            self.name = self.path.split('/')[-1]
            self.local_path = os.path.join(self.base_dir, self.path[1:].replace('/', os.path.sep))
        
        if not os.path.exists(self.local_path):
            self._set_base_use_default()
        self._set_extra()

    def _rectify(self, path):
        """ Return regulated path.
            rectify input path to regular path such as '/','/home', '/home/data'
        """
        if path is None or path == '':
            path = '/'
        if path == '/':
            return path
        if not path[0] == '/':
            path = '/' + path
        if path[-1:] == '/':
            path = path[:-1]
        return path
    
    def _set_base_use_default(self):
        """ Set base attr with default value.
            base attrs: `path`, `name`, `local_path`
        """
        self.path = '/'
        self.name = 'Home'
        self.local_path = self.base_dir

    def _set_extra(self):
        """ Set extra attributes after set `local_path`
        """
        node_info = os.stat(self.local_path)
        self.size = _kb_size(node_info.st_size)
        self.create = _standard_timestr(node_info.st_ctime)
        self.visit = _standard_timestr(node_info.st_atime)
        self.modify = _standard_timestr(node_info.st_mtime)

    @property
    def layer_path(self):
        """ Return list for path navigation
        """
        paths = list()
        if self.path == '/':
            paths.append(dict(name='Home', path='/'))
            return paths
        path_names = self.path.split('/')
        for i in range(len(path_names)):
            _name = path_names[i]
            if i == 0:
                paths.append(dict(name='Home', path='/'))
            else:
                d = dict(name=_name, path='/'.join(path_names[:i+1]))
                paths.append(d)
        return paths

    @property
    def children(self):
        """ Return children node list.
        """
        child_list = list()
        for _name in os.listdir(self.local_path):
            if self.path == '/':
                path = '/' + _name
            else:
                path = self.path + '/' + _name
            node = Node(path)
            child_list.append(node)
        return child_list
    
    @property
    def tree(self):
        """ Return tree list for jstree.
        """
        node_tree = list()
        node_tree.append(dict(id=self.path, parent="#", text=self.name, state=dict(opened=True)))
        for root, dirs, files in os.walk(self.local_path):
            for dname in dirs:
                _suffix = root[len(self.local_path):].replace(os.path.sep, '/')
                _parent = self.path + '/' + _suffix
                if _suffix == '':
                    _parent = self.path
                else:
                    if self.path =='/':
                        _parent = _suffix
                    else:
                        _parent = self.path + _suffix

                if _parent == '/':
                    _path = '/' + dname
                else:
                    _path = _parent + '/' + dname
                d = dict(id=_path, parent=_parent, text=dname)
                node_tree.append(d)
        return node_tree