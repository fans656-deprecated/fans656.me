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
        self.ctime = None

def session_object():
    res = Session()
    cookie_value = get_session()
    if exists(cookie_value):
        res.username = db.query(
            'match (s:Session{cookie_value: {cookie_value}}) '
            'return s.username', {
                'cookie_value': cookie_value,
            }, one=True)
    return res


def get_session():
    return request.cookies.get('session', None)

def exists(cookie_value):
    return db.query(
        'match (s:Session{cookie_value: {cookie_value}}) return count(s)', {
            'cookie_value': cookie_value,
        }, one=True) != 0

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
    expires_at = db.query(
        'match (s:Session) where s.cookie_value = {cookie_value} '
        'return s.expires_at ', {
            'cookie_value': cookie_value,
        }, one=True)
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
