import os, binascii
import random
from datetime import datetime, timedelta

from flask import request

import config
import db

class Session(object):

    def __init__(self):
        self.username = ''

def session_object():
    r = Session()
    id = get_session()
    if is_existed(id):
        r.username = db.queryone('select username from sessions where id = %s', (id,))
    return r

def get_session():
    return request.cookies.get('session', None)

def is_existed(id):
    return bool(db.queryone('select count(*) from sessions where id = %s',
                         (id,)))

def new_session(username):
    while True:
        id = binascii.hexlify(os.urandom(32))
        if not is_existed(id):
            break
    now = datetime.now()
    duration = timedelta(days=config.session_duration_days)
    db.execute('insert into sessions (id, username, ctime, expires) values'
              '(%s, %s, %s, %s)', (id, username, now, now + duration))
    return id

def logged_in():
    if random.random() < config.sweep_expires_probability:
        db.execute('delete from sessions where expires < %s', (datetime.now()))
    id = get_session()
    if not id:
        return False
    expires = db.queryone('select expires from sessions where id = %s', (id,))
    if not expires:
        return False
    if expires < datetime.now():
        db.execute('delete from sessions where id = %s', (id,))
        return False
    # refresh expires
    if random.random() < 0.1:
        duration = timedelta(days=config.session_duration_days)
        db.execute('update sessions set expires = %s where id = %s',
                  (expires + duration, id))
    return True

def del_session():
    id = get_session()
    if not is_existed(id):
        return False
    db.execute('delete from sessions where id = %s', (id,))
    return True
