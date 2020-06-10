#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
#from flask import current_app
#from .utils import unit_size, standard_timestr, is_binary_file

class Node(object):
    """ Node is an abstract model, 
        a folder or a file can be a Node.
        Node base attributes:
        :attr id:           node id, a string.
        :attr name:         node name, a string.
        :attr base_dir:     absolute local path of base directory.
        :attr path:         node relative path use linux-style to 'base_dir', such as '/', '/home', '/home/data'.
        :attr parent_path:  node parent path, relative path, if node path is '/', parent_path will set to be `None`.
        :attr local_path:   node local path.
        :attr type:         node type name.
    """
    __type__ = 'Node'

    def __init__(self, path='/', base_dir=None):
        self.name = ''
        self.base_dir = base_dir
        self.path = path
        self.parent_path = None
        self.local_path = None

    @property
    def id(self):
        return self.path.replace('/', '|')

    @property
    def type(self):
        return self.__class__.__type__

class DirectoryNode(Node):
    __type__ = 'Directory'

    def children(self):
        pass
    
    def search(self, keywords):
        pass

class FileNode(Node):
    __type__ = 'File'

class TextFileNode(FileNode):
    __type__ = 'Text File'

class BinarayFileNode(FileNode):
    __type__ = 'Binaray File'

class AudioFileNode(BinarayFileNode):
    __type__ = 'Audio File'

class VideoFileNode(BinarayFileNode):
    __type__ = 'Video File'

class PhotoFileNode(BinarayFileNode):
    __type__ = 'Photo File'

class NodeContext(object):
    def __init__(self, path, base_dir):
        self.node = Node(path, base_dir)

class NodeFactory(object):
    @classmethod
    def create(cls, path='/', base_dir=None):
        return Node(path, base_dir)

if __name__ == '__main__':
    n = VideoFileNode('/home/zhazh/video')
    print(n.id)
    print(PhotoFileNode().type)
    print(isinstance(n, DirectoryNode))
    print(BinarayFileNode.__base__.__name__)