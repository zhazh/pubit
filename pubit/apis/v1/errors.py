# -*- coding: utf-8 -*-
"""
.apis.v1.errors
===============
define errors
"""
from flask import jsonify

class AjaxError(object):
    def __init__(self, code, msg, status_code):
        self.code = code
        self.msg = msg
        self.status_code = status_code
    
    @property
    def dic(self):
        return dict(code=self.code, msg=self.msg)

    @property
    def json_resp(self):
        return jsonify(dict(code=self.code, msg=self.msg)), self.status_code

UnauthenticatedError = AjaxError(code=1, msg='Unauthenticated.', status_code=403)
ServerError = AjaxError(code=2, msg='Server occoured an exception.', status_code=500)
