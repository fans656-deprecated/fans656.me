import os
import hashlib
import binascii
import functools

import db
from util import error_response, utcnow, logger
import session_util
from errors import Forbidden_403


def try_auth(username, password):
    assert exists(username), 'user does not exist'
    salt, expected_hashed_password = db.query(
        'match (u:User{username: {username}}) '
        'return u.salt, u.hashed_password', {
            'username': username
        }, rows=1)
    _, got_hashed_password = get_hashed_salt_and_password(password, salt)
    assert got_hashed_password == expected_hashed_password, 'invalid auth'


def try_register(username, password):
    #logger(username=username, password=password)
    assert not exists(username), 'username already taken!'
    salt, hashed_password = get_hashed_salt_and_password(password)
    db.execute(
        'create (u:User{'
            'username: {username}, '
            'salt: {salt}, '
            'hashed_password: {hashed_password}, '
            'ctime: {ctime}'
        '})', {
            'username': username,
            'salt': salt,
            'hashed_password': hashed_password,
            'ctime': utcnow(),
        }
    )

def create_user(username, password):
    salt, hashed_password = get_hashed_salt_and_password(password)
    return db.execute('''
        create (n:User{
            username: {username},
            salt: {salt},
            hashed_password: {hashed_password},
            ctime: {ctime}
        })
               '''
        , {
            'username': username,
            'salt': salt,
            'hashed_password': hashed_password,
            'ctime': utcnow(),
        }
    )


def delete_user(username):
    return db.execute(
        'match (n:User{username: {username}}) detach delete n'
        , {
            'username': username,
        }
    )


def exists(username):
    return db.query(
        'match (n:User{username: {username}}) return count(n)'
        , {'username': username}, one=True) != 0


def get_hashed_salt_and_password(password, salt=None):
    if salt is None:
        salt = binascii.hexlify(os.urandom(32))
    hashed_pwd = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    hashed_pwd = binascii.hexlify(hashed_pwd)
    return salt, hashed_pwd


def current_user():
    s = session_util.session_object()
    username = s.username
    user = db.query('match (u:User{username: {username}}) return u',
                    {'username': username}, one=True)
    user = user or {}
    if s.username:
        return {
            'username': user['username'],
            'ctime': user['ctime'],
            'avatar_url': user.get('avatar_url'),
        }
    else:
        return None


def require_login(viewfunc):
    @functools.wraps(viewfunc)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return error_response('you are not logged in', Forbidden_403)
        return viewfunc(*args, **kwargs)
    return wrapper


def require_me_login(viewfunc):
    @functools.wraps(viewfunc)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user['username'] != 'fans656':
            return error_response('you are not "fans656"', Forbidden_403)
        return viewfunc(*args, **kwargs)
    return wrapper
