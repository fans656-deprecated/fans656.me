import os
from base64 import decodestring

import flask

import db
import conf
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
            'ctime': user['ctime'],
            'avatar_url': user['avatar_url'],
        },
    })


def get_avatar(username):
    avatar_url = db.query_one(
        'match (u:User{username: {username}}) return u.avatar_url', {
            'username': username,
        })
    return success_response({'avatar_url': avatar_url})


def post_avatar(username):
    data = flask.request.json['data']
    filetype, data = data.split(';')
    ext = filetype.split('/')[1]
    data = data.split(',')[1]

    path = 'user/{}/meta/avatar.{}'.format(username, ext)
    fpath = util.rooted_path(conf.FILES_ROOT, path)

    dirpath = os.path.dirname(fpath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    with open(fpath, 'wb') as f:
        f.write(data.decode('base64'))

    avatar_url = '/file/' + path
    user = db.execute(
        'match (u:User{username: {username}}) '
        'set u.avatar_url = {avatar_url}', {
            'username': username,
            'avatar_url': avatar_url,
        })
    return success_response({
        'avatar_url': avatar_url,
    }) if user else error_response('not found')
