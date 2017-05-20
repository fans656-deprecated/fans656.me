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

def require_login(f):
    @functools.wraps(f)
    def f_(*args, **kwds):
        s = session.session_object()
        if not s.username:
            return redirect('/login', 302)
        return f(s, *args, **kwds)
    return f_

def ok(data={}):
    res = {'status': 'ok'}
    res.update(data)
    return jsonify(**res)

def error(detail):
    return jsonify(**{
        'status': 'error',
        'detail': detail,
    })
