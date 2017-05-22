from flask import render_template, request

import session
import db
from utils import ok, error, allow_public_access

def get_clip_data(username):
    return db.queryone('select data from clips where username = %s',
                       (username,)) or ''

@allow_public_access
def clip(session):
    data = get_clip_data(session.username).decode('utf8')
    return render_template('clip.html', data=data)

@allow_public_access
def clip_get(session):
    return get_clip_data(session.username)

@allow_public_access
def clip_save(session):
    data = request.get_json(force=True, silent=True).get('data', None)
    if data is None:
        return error('no data')
    data = data.encode('utf8')
    db.execute('insert into clips (username, data) values '
               '(%s, %s) on duplicate key update data = %s',
               (session.username, data, data))
    return ok()
