import os
from datetime import datetime
from base64 import b64encode
import hashlib

from flask import (
    Flask, request, Response, redirect, jsonify,
    render_template, url_for,
)

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def hex_repr(s):
    return ''.join('{:02x}'.format(ord(c)) for c in s)

def salted(pwd):
    salt = b64encode(os.urandom(8))
    m = hashlib.md5()
    m.update(salt + pwd)
    pwd = hex_repr(m.digest())
    return salt, pwd

def md5hash(s):
    m = hashlib.md5()
    m.update(s)
    return hex_repr(m.digest())

users = {
    'a': salted('b'),
}

sessions = {
}

class AuthFailed(Exception): pass

INVALID_CREDENTIAL = 'username or password incorrect'

app = Flask(__name__)

def ok(data={}):
    res = {'status': 'ok'}
    res.update(data)
    return jsonify(**res)

def challenge(username, detail):
    return ok({
        'status': 'auth',
        'salt': get_salt(username),
        'nonce': b64encode(os.urandom(16)),
        'detail': detail,
    })

def error(detail):
    return jsonify(**{'status': 'error', 'detail': detail})

def get_salt(username):
    try:
        return users[username][0]
    except KeyError:
        return None

def get_password(username):
    try:
        return users[username][1]
    except KeyError:
        return None

def do_auth(username):
    nonce = request.form.get('nonce')
    response = request.form.get('response')

    if not username:
        raise AuthFailed('username required')
    if not nonce:
        raise AuthFailed('nonce required')
    if not response:
        raise AuthFailed('response required')

    password = get_password(username)
    if password is None:
        raise AuthFailed(INVALID_CREDENTIAL)
    print 'User:', username, password

    m = hashlib.md5()
    m.update('{}:{}:{}'.format(username, nonce, password))
    valid_response = hex_repr(m.digest())
    print 'expect:', valid_response
    print 'got:   ', response
    if response != valid_response:
        raise AuthFailed(INVALID_CREDENTIAL)

    resp = ok()
    resp.set_cookie('session', value=new_session(username))
    return resp

def new_session(username):
    now = datetime.now().strftime(DATETIME_FORMAT)
    session = md5hash(str(len(sessions)) + username + now + b64encode(os.urandom(16)))
    sessions[session] = {
        'username': username,
        'login-at': now,
    }
    return session

def require_login(f):
    def f_(*args, **kwds):
        session = request.cookies.get('session')
        if session not in sessions:
            return render_template('login.html', logged_in=False)
        return f(session, *args, **kwds)
    return f_

@app.route('/')
@require_login
def index(session):
    session = sessions[session]
    username = session['username']
    login_at = session['login-at']
    print 'logged in'
    return render_template('index.html',
                           logged_in=True,
                           username=username,
                           login_at=login_at,
                           now=datetime.now().strftime(DATETIME_FORMAT))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session = request.cookies.get('session')
    username = request.form.get('username')
    if session in sessions:
        return redirect('/', 302)
    try:
        res = do_auth(username)
        return res
    except AuthFailed as e:
        return challenge(username, e.message)

@app.route('/logout')
def logout():
    session = request.cookies.get('session')
    if session in sessions:
        del sessions[session]
    else:
        return '<p>looks like you are not logged in</p>'
    resp = Response('logged out')
    resp.set_cookie('session', value='')
    return resp

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
