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
    data.update({'errno': 0})
    return jsonify(**data)

def error(detail, status_code=400):
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

def notfound():
    return error('not found', 404)

_datetime_format = '%Y-%m-%d %H:%M:%S.%f'

def strftime(dt):
    return dt.strftime(_datetime_format)

def strptime(s):
    return datetime.strptime(s, _datetime_format)
