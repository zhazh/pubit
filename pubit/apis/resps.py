# -*- coding: utf-8 -*-
"""
.apis.resps
====================
define json data response for ajax method.
"""
from flask import jsonify

class AjaxResp(object):
    def __init__(self, code, msg, status_code):
        self.code = code
        self.msg = msg
        self.status_code = status_code
    
    @property
    def dic(self):
        return dict(code=self.code, msg=self.msg)

    @property
    def jsonify(self):
        return jsonify(self.dic), self.status_code

class RespSuccess(AjaxResp):
    def __init__(self):
        #: Return with http status: 200, OK.
        super().__init__(0, 'Success', 200)

class RespUnauthenticated(AjaxResp):
    def __init__(self):
        #: Return with http status: 403, Forbidden.
        super().__init__(1, 'Unauthenticated.', 403)

class RespServerWrong(AjaxResp):
    def __init__(self):
        #: Return with http status: 500, Internal error.
        super().__init__(2, 'Server occoured an exception.', 500)

class RespArgumentWrong(AjaxResp):
    def __init__(self, arg_name, extra=None):
        #: Return with http status: 400, Bad Request.
        if extra:
            super().__init__(3, "Argument '%s' %s."%(arg_name, extra), 400)
        super().__init__(3, "Argument '%s' wrong."%arg_name, 400)