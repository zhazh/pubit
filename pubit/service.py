# -*- coding: utf-8 -*-
"""
.service
=================
App middle service.
"""
import os
import time
import codecs
from datetime import datetime
from flask import current_app

def _unit_size(size):
    """ Convert Byte size to KB/MB/GB/TB.
    """
    units = ['KB', 'MB', 'GB', 'TB']
    i = 0
    size = size / 1024
    while size >= 1024 and i<(len(units)-1):
        i = i + 1
        size = size / 1024
    return '%.2f %s'%(size, units[i])

def _kb_size(size):
    return '%.2f KB' %(size/1024)

def _standard_timestr(localtime):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(localtime))

_TEXT_BOMS = (
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
    codecs.BOM_UTF8,
)

def _is_binary_file(filepath):
    with open(filepath, 'rb') as file:
        initial_bytes = file.read(8192)
        file.close()
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) and b'\0' in initial_bytes

class _File(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def typename(self):
        try:
            if os.path.isdir(self.filepath):
                return 0, 'Directory'
            else:
                path, filename = os.path.split(self.filepath)
                suffix = filename.split('.')[-1].lower()
                if suffix in ('mp3', 'wav'):
                    return 1, 'Audio File'
                elif suffix in ('mp4', 'mov'):
                    return 2, 'Video File'
                else:
                    if _is_binary_file(self.filepath):
                        return 3, 'Binaray File'
                    else:
                        return 4, 'Text File'
        except Exception as e:
            return -1, 'Unknow File'

class Node(object):
    def __init__(self, base_dir=None, path='/'):
        """ Create node attributes.
            :attr base_dir:     absolute local path of base directory.
            :attr path:         path relactive to base directory used web path style, such as '/', '/home', '/home/data'.
            :attr name:         node name, root path name is 'Home'.
            :attr local_path:   absolute local path of node.
            :attr size:         node size.
            :attr create:       node create time.
            :attr visit:        node last visit time.
            :attr modify:       node last modify time.
            :attr type:         node type, such as 'directory', 'audio file'
        """
        self.base_dir = os.path.normpath(base_dir if base_dir else current_app.config['ADMIN_HOME'])
        if not os.path.isdir(self.base_dir):
            raise TypeError("Invalid argument 'base_dir'")
        
        self.path = self._regulate_path(path)
        if self.path == '/':
            self.name = 'Home'
        else:
            self.name = os.path.split(self.path)[-1]
        valid_path = list(filter(lambda p: p!='', self.path.split('/')))
        self.local_path = os.path.join(self.base_dir, *valid_path)
        if not os.path.exists(self.local_path):
            raise TypeError("Invalid argument 'path'")
        self._set_extra()

    def _regulate_path(self, path):
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

    def _set_extra(self):
        """ Set extra attributes after set attr `local_path`.
        """
        node_info = os.stat(self.local_path)
        self.size = _unit_size(node_info.st_size)
        self.create = _standard_timestr(node_info.st_ctime)
        self.visit = _standard_timestr(node_info.st_atime)
        self.modify = _standard_timestr(node_info.st_mtime)
        self.type = _File(self.local_path).typename()

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
        """ Return child node list if node is directory.
        """
        child_list = list()
        for _name in os.listdir(self.local_path):
            if self.path == '/':
                path = '/' + _name
            else:
                path = self.path + '/' + _name
            node = Node(base_dir=self.base_dir, path=path)
            child_list.append(node)
        return child_list
    
    @property
    def tree(self):
        """ Return recursive sub directory tree if node is directory.
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