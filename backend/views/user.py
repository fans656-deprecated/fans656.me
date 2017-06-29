import flask

import utils
from utils import success_response, error_response


def post_login():
    username = flask.request.json.get('username', '')
    password = flask.request.json.get('password', '')
    utils.user.try_auth(username, password)

    resp = success_response()
    resp.set_cookie('session', utils.session.new_session(username))
    return resp


def get_logout():
    if utils.session.del_session():
        return success_response()
    else:
        return error_response('delete session failed')


def get_me():
    return success_response({
        'user': utils.session.current_user()
    })
