import flask

import util
import user_util
import session_util
from util import success_response, error_response


def post_login():
    username = flask.request.json.get('username', '')
    password = flask.request.json.get('password', '')
    user_util.try_auth(username, password)

    resp = success_response()
    resp.set_cookie('session', session_util.new_session(username))
    return resp


def post_register():
    username = flask.request.json.get('username', '')
    password = flask.request.json.get('password', '')
    user_util.try_register(username, password)

    resp = success_response()
    resp.set_cookie('session', session_util.new_session(username))
    return resp

def get_logout():
    if session_util.del_session():
        return success_response()
    else:
        return error_response('delete session failed')


def get_me():
    return success_response({
        'user': session_util.current_user()
    })
