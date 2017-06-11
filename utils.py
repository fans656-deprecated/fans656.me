import functools
from datetime import datetime

from flask import redirect, jsonify

import session

def allow_public_access(f):
    @functools.wraps(f)
    def f_(*args, **kwds):
        s = session.session_object()
        if not s.username:
            s.username = 'guest'
        return f(s, *args, **kwds)
    return f_

def require_login(f):
    @functools.wraps(f)
    def f_(*args, **kwds):
        s = session.session_object()
        if not s.username:
            return error('you are not logged in')
        return f(s, *args, **kwds)
    return f_

def ok(data=None):
    if data is None:
        data = {}
    elif isinstance(data, (str, unicode)):
        data = {'detail': data}
    data.update({'errno': 0, 'ok': True})
    return jsonify(**data)

def error(detail):
    resp = jsonify(**{
        'errno': 400,
        'ok': False,
        'detail': detail,
    })
    return resp

_datetime_format = '%Y-%m-%d %H:%M:%S.%f'

def strftime(dt):
    return dt.strftime(_datetime_format)

def strptime(s):
    return datetime.strptime(s, _datetime_format)
