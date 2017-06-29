import flask

import utils
from utils import success_response, error_response
import session


def post_login():
    username = flask.request.json.get('username', '').encode('utf8')
    password = flask.request.json.get('password', '').encode('utf8')
    utils.user.try_login(username, password)

    resp = success_response()
    resp.set_cookie('session', session.new_session(username))
    return resp


def get_logout():
    if session.del_session():
        return success_response()
    else:
        return error_response('delete session failed')


def get_me():
    return success_response({
        'user': session.current_user()
    })
