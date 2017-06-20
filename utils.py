import functools
from datetime import datetime

from flask import redirect, jsonify

import session

class NotFound(Exception):

    pass

class Response(Exception):

    def __init__(self, data):
        super(Response, self).__init__('Response with data: {}'.format(data))
        self.data = data

def allow_public_access(f):
    @functools.wraps(f)
    def f_(*args, **kwds):
        s = session.session_object()
        if not s.username:
            s.username = 'guest'
        return f(s, *args, **kwds)
    return f_

# TODO: non usable
def require_login(*args, **login_info):
    def wrapper(*args, **kwds):
        s = session.session_object()
        username = login_info.get('username')
        if username and s.username != username:
            return error_response('you are not {}'.format(username))
        if not s.username:
            return error_response('you are not logged in')
        return f(s, *args, **kwds)
    if len(args) == 1 and callable(args[0]):
        f = args[0]
        return functools.wraps(f)(wrapper)
    else:
        return lambda f: functools.wraps(f)(wrapper)

require_me_login = require_login(username='fans656')

def success_response(data=None):
    if data is None:
        data = {}
    elif isinstance(data, (str, unicode)):
        data = {'detail': data}
    data.update({'errno': 0})
    return jsonify(**data)

def error_response(detail, status_code=400):
    if isinstance(detail, dict):
        data = detail
        detail = detail.get('detail', '')
    else:
        data = {}
    data.update({
        'errno': status_code,
        'detail': detail,
    })
    resp = jsonify(**data)
    resp.status_code = status_code
    return resp

_datetime_format = '%Y-%m-%d %H:%M:%S.%f'

def strftime(dt):
    return dt.strftime(_datetime_format)

def strptime(s):
    return datetime.strptime(s, _datetime_format)

def check(pred, errmsg):
    assert pred, errmsg
