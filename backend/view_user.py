import flask

import db
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


def get_profile(username):
    user = db.query_node('match (u:User{username: {username}}) return u', {
        'username': username,
    })
    return success_response({
        'user': {
            'username': user['username'],
            'joined_at': user['created_at'],
            'avatar': user.get('avatar'),
        },
    })


def get_avatar(username):
    data = db.query_one(
        'match (u:User{username: {username}}) return u.avatar', {
            'username': username,
        })
    return data or ''


def post_avatar(username):
    data = flask.request.json['data']
    user = db.execute(
        'match (u:User{username: {username}}) '
        'set u.avatar = {data}', {
            'username': username,
            'data': data,
        })
    return success_response() if user else error_response('not found')
