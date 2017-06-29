# coding: utf-8
import os
import functools
import traceback
from datetime import datetime

import flask
from flask import redirect, jsonify
from dateutil.parser import parse as parse_datetime

import session
from utils import user


class Response(Exception):

    def __init__(self, data):
        super(Response, self).__init__('Response with data: {}'.format(data))
        self.data = data


def handle_exceptions(viewfunc):
    @functools.wraps(viewfunc)
    def wrapper(*args, **kwargs):
        try:
            return viewfunc(*args, **kwargs)
        except Exception as e:
            return error_response(e)
    return wrapper


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

def require_me_login(f):
    @functools.wraps(f)
    def f_(*args, **kwargs):
        username = session.session_object().username
        if username != 'fans656':
            return error_response('you are not {}'.format(username))
        if not username:
            return error_response('you are not logged in')
        return f(*args, **kwargs)
    return f_

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
    elif isinstance(detail, Exception):
        detail = traceback.format_exc(detail)
        print detail
        data = {}
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

def to_unicode(s, what='unknown'):
    try:
        if isinstance(s, unicode):
            return s
        elif isinstance(s, str):
            return s.decode('utf-8')
        else:
            raise Exception('can not convert to unicode')
    except Exception as e:
        raise ValueError('{} should be unicode, but got {}: {}\n\n{}'.format(
            what, type(s), repr(s), indented_exception(e)
        ))

def to_datetime(o, what='unknown'):
    try:
        if isinstance(o, datetime):
            return o
        s = to_unicode(o, what)
        return parse_datetime(s)
    except Exception as e:
        raise ValueError('{} should be datetime, but got {}: {}\n{}'.format(
            what, type(o), o, indented_exception(e)
        ))


def indented_exception(exc):
    return '\n'.join(' ' * 4 + '| ' + line
                     for line in traceback.format_exc(exc).split('\n'))


def send_from_directory(*paths):
    fpath = os.path.join(*paths)
    fpath = os.path.abspath(fpath)
    if not fpath.startswith(paths[0]):
        raise errors.NotAllowed('are you up to something?')
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    return flask.send_from_directory(dirname, fname)


def utcnow():
    return str(datetime.utcnow()) + ' UTC'


if __name__ == '__main__':
    pass
    #print to_unicode('hi')
    #print to_unicode(u'hi')
    #print to_unicode(u'中国'.encode('gbk'))
    #print to_unicode(3)
    print to_datetime(datetime.now())
    #print to_datetime('2017-6-18 22:18:03+08:00')
    print to_datetime(3)
