# -*- coding: utf-8 -*-
"""
.service
========================
Directory action service.
"""
import os
from collections import defaultdict
from shutil import (copy, copytree, move, rmtree, make_archive)

class Message(object):
    """ Message type support emitted with arguments.
    """
    def __init__(self, center, name):
        self.name = name
        self.center = center

    def send(self, sender, **extra):
        """ Emitted an message with arguments.
            :param sender: describe who send the message.
            :type sender: object.
        """
        self.center._notify(self, sender, **extra)

class MessageCenter(object):
    """ Hold message operation. 
        - use :meth:`MessageCenter.message` to define an message type.
        - use :meth:`MessageCenter.sub` for recipient to subscribe to the message.
        - use :meth:`MessageCenter.clear_sub_on` to clear all recipients on the message.
        - use :meth:`MessageCenter.cancel_sub_for` for the recipient to cancel message subscribed.
    """
    def __init__(self):
        #: _dispatcher mapping messages and recipients.
        self._dispatcher = defaultdict(list)

    def message(self, name):
        """ Define an message type.
            :param name: message name.
            :type name: string
        """
        return Message(self, name)

    def sub(self, msg, recipient):
        """ Recipient subscribe to message
            :param msg: the :class: `Message` object to subscribe to.
            :type msg: :class: `Message`
            :param recipient: the object recived msg.
            :type recipient: :object of subclass of :class: `Recipient` 
        """
        if recipient not in self._dispatcher.keys():
            self._dispatcher[msg].append(recipient)
    
    def clear_sub_on(self, msg):
        """ Clear all recipients on message :param:`msg`.
        """
        self._dispatcher[msg].clear()
    
    def cancel_sub_for(self, recipient):
        """ Cancel subscribed messages for recipient.
        """
        for msg, recipients in self._dispatcher.items():
            if recipient in recipients:
                self._dispatcher[msg].remove(recipient)

    def _notify(self, msg, sender, **extra):
        for recipient in self._dispatcher[msg]:
            if isinstance(recipient, Recipient):
                recipient._handle_msg(msg, sender, **extra)

class Recipient(object):
    """ Interface class described recipient.
    """
    def _handle_msg(self, message, sender, **extra):
        try:
            self.on_receive(sender, **extra)
        except KeyError as e:
            raise TypeError("send message:'%s' miss argument %s"%(message.name, e))
    
    def on_receive(self, sender, **extra):
        pass

class _TaskMeta(type):
    def __new__(cls, name, bases, attrs):
        if '_Task' in (base.__name__ for base in bases):
            _msg_name = attrs.get('__msg_name__', None)
            if _msg_name is None:
                raise AttributeError("class '%s' has not class attribute '__msg_name__'"%name)
            subclass = type.__new__(cls, name, bases, attrs)
            _Task.__msg_map__[_msg_name] = subclass
            return subclass
        return type.__new__(cls, name, bases, attrs)

class _Task(Recipient, metaclass=_TaskMeta):
    __msg_map__ = dict()

    @classmethod
    def create(cls, name):
        subclass = cls._msg_map().get(name, None)
        if subclass:
            return subclass()
        return cls()

    def on_receive(self, sender, **extra):
        self.run(**extra)

    def run(self, **kw):
        pass

    @classmethod
    def _msg_map(cls):
        return cls.__msg_map__

class _TaskNew(_Task):
    __msg_name__ = 'new'

    def run(self, **kw):
        target = kw["target"]
        os.makedirs(target)

class _TaskDelete(_Task):
    __msg_name__ = 'delete'
    
    def run(self, **kw):
        target = kw["target"]
        if os.path.isdir(target):
            rmtree(target)
        else:
            os.remove(target)

class _TaskCopy(_Task):
    __msg_name__ = 'copy'
    
    def run(self, **kw):
        src = kw["src"]
        dst = kw["dst"]
        if os.path.isdir(src):
            copytree(src, dst)
        else:
            copy(src, dst)

class _TaskMove(_Task):
    __msg_name__ = 'move'
    
    def run(self, **kw):
        src = kw["src"]
        dst = kw["dst"]
        move(src, dst)

class _TaskCompress(_Task):
    __msg_name__ = 'compress'
    
    def run(self, **kw):
        targets = kw["targets"]
        dst_name = kw["dst_name"]
        tmpdir = kw["temp_dir"]
        dst_dir = os.path.join(tmpdir, dst_name)
        os.makedirs(dst_dir)
        for target in targets:
            src = target
            dst = dst_dir
            if os.path.isdir(src):
                dst = os.path.join(dst, os.path.split(src)[-1])
                copytree(src, dst)
            else:
                copy(src, dst)
        make_archive(dst_dir, "zip", root_dir=dst_dir)
        rmtree(dst_dir)

class Service(object):
    node_messages = _Task._msg_map().keys()

    def __init__(self):
        self._center = MessageCenter()
        self._msgs = dict()
        for _msg_name in self.__class__.node_messages:
            msg = self._center.message(_msg_name)
            task = _Task.create(_msg_name)
            self._center.sub(msg, task)
            self._msgs[_msg_name] = msg

    def send(self, msg_name, **extra):
        try:
            self._msgs[msg_name].send(self, **extra)
        except KeyError:
            raise TypeError("message name:'%s' not support"%msg_name)

class GlobalService(object):
    service = Service()

    @classmethod
    def send(cls, msg_name, **extra):
        cls.service.send(msg_name, **extra)


#: unit test.
if __name__ == '__main__':
    print('service test.')
    GlobalService.send('copy', src="/home/zhazh/temp/home/1", dst="/home/zhazh/temp/bin_home/1")
    #GlobalService.send('move', src="/home/zhazh/temp/1", dst="/home/zhazh/temp/mv/1")
    #GlobalService.send('new', target='/home/zhazh/temp/good')
    #GlobalService.send('new', target='/home/zhazh/temp/good/stuff')
    #GlobalService.send('new', target='/home/zhazh/temp/good/stuff/guys')
    #GlobalService.send('delete', target='/home/zhazh/temp/good/stuff/guys')
    #GlobalService.send('copy', src="/home/zhazh/temp/good/stuff", dst="/home/zhazh/temp/stuff_copy")
    #GlobalService.send('new', target='/home/zhazh/temp/good/mayday')
    #GlobalService.send('move', src="/home/zhazh/temp/good/mayday", dst="/home/zhazh/temp/mayday")
    #GlobalService.send('compress', targets=["/home/zhazh/temp/good", "/home/zhazh/temp/mayday"], dst_name="good_mayday", temp_dir="/home/zhazh/temp")