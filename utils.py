import functools

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

def require_login(*args, **login_info):
    def wrapper(*args, **kwds):
        s = session.session_object()
        username = login_info.get('username')
        if username and s.username != username:
            return error('you are not {}'.format(username))
        if not s.username:
            return redirect('/login', 302)
        return f(s, *args, **kwds)
    if len(args) == 1 and callable(args[0]):
        f = args[0]
        return functools.wraps(f)(wrapper)
    else:
        return lambda f: functools.wraps(f)(wrapper)

def ok(data={}):
    res = {'status': 'ok'}
    res.update(data)
    return jsonify(**res)

def error(detail, errno=400):
    resp = jsonify(**{
        'errno': errno,
        'status': 'error',
        'detail': detail,
    })
    resp.status_code = errno
    return resp
