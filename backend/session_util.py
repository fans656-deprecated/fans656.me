import os, binascii
import random
from datetime import datetime, timedelta

from flask import request

import db
import conf
from util import utcnow, logger

class Session(object):

    def __init__(self):
        self.username = ''
        self.created_at = None

def session_object():
    res = Session()
    cookie_value = get_session()
    if exists(cookie_value):
        res.username = db.query_one(
            'match (s:Session{cookie_value: {cookie_value}}) '
            'return s.username', {
                'cookie_value': cookie_value,
            }
        )
    return res

def current_user():
    s = session_object()
    username = s.username
    user = db.query_node('match (u:User{username: {username}}) return u',
                         {'username': username})
    logger(user=user)
    user = user or {}
    if s.username:
        return {
            'username': user['username'],
            'created_at': user['created_at'],
            'avatar_url': user.get('avatar_url'),
        }
    else:
        return None

def get_session():
    return request.cookies.get('session', None)

def exists(cookie_value):
    return db.query_one(
        'match (s:Session{cookie_value: {cookie_value}}) return count(s)', {
            'cookie_value': cookie_value,
        }
    ) != 0

def gen_new_cookie_value():
    while True:
        cookie_value = binascii.hexlify(os.urandom(32))
        if not exists(cookie_value):
            return cookie_value

def new_session(username):
    cookie_value = gen_new_cookie_value()
    expires_at = expires_at_from_now()
    db.execute(
        'create (s:Session{ '
            'cookie_value: {cookie_value},'
            'username: {username},'
            'expires_at: {expires_at}'
        '})', {
            'cookie_value': cookie_value,
            'username': username,
            'expires_at': expires_at,
        }
    )
    return cookie_value

def expires_at_from_now():
    now = datetime.utcnow()
    duration = timedelta(days=conf.session_duration_days)
    expires_at = str(now + duration) + ' UTC'
    return expires_at

def is_logged_in():
    if random.random() < conf.sweep_expires_probability:
        db.execute('match (s:Session) where expires_at < {now} delete s', {
            utcnow()
        })
    expires_at = db.query_one(
        'match (s:Session) where s.cookie_value = {cookie_value} '
        'return s.expires_at ', {
            'cookie_value': cookie_value,
        })
    if expires_at < utcnow():
        return False
    db.execute(
        'match (s:Session{cookie_value: {cookie_value}}) '
        'set s.expires_at = {expires_at}', {
            'expires_at': expires_at_from_now()
        }
    )
    return True

def del_session():
    cookie_value = get_session()
    if not exists(cookie_value):
        return False
    db.execute('match (s:Session{cookie_value: {cookie_value}}) delete s', {
        'cookie_value': cookie_value,
    })
    return True
