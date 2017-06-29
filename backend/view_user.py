import flask

import util
from util import success_response, error_response


def post_login():
    username = flask.request.json.get('username', '')
    password = flask.request.json.get('password', '')
    util.user.try_auth(username, password)

    resp = success_response()
    resp.set_cookie('session', util.session.new_session(username))
    return resp


def get_logout():
    if util.session.del_session():
        return success_response()
    else:
        return error_response('delete session failed')


def get_me():
    return success_response({
        'user': util.session.current_user()
    })
