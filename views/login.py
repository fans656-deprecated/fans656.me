from flask import render_template, request, redirect

import user
import session
from utils import ok, error

def register():
    if session.logged_in():
        return ok({'detail': 'you may wanna logout first'})
    if request.method == 'GET':
        return render_template('register.html', no_nav_right=True)
    elif request.method == 'POST':
        username = request.form.get('username', '').encode('utf8')
        password = request.form.get('password', '').encode('utf8')
        try:
            user.register(username, password)
            return ok()
        except user.UserExisted as e:
            return error(e.message)

def login():
    if session.logged_in():
        return ok({'detail': 'you are logged in'})
    if request.method == 'GET':
        return render_template('login.html', no_nav_right=True)
    elif request.method == 'POST':
        username = request.form.get('username', '').encode('utf8')
        password = request.form.get('password', '').encode('utf8')
        try:
            user.login(username, password)
            resp = ok()
            resp.set_cookie('session', session.new_session(username))
            return resp
        except user.InvalidAuth as e:
            return error(e.message)

def logout():
    if not session.del_session():
        return 'you are not logged in'
    resp = redirect('/', 302)
    resp.set_cookie('session', value='')
    return resp

def profile(username):
    s = session.session_object()
    s.visitor = username
    return render_template('user.html', session=s)
