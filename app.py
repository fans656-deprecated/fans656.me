import os
import json
from datetime import datetime

import flask
from flask import request
from flask_cors import CORS

import session
import db
import user
import utils
import config
from utils import (
    ok, error, require_login, allow_public_access,
    strftime, strptime,
)

build_dir = './frontend/build'

app = flask.Flask(__name__, static_folder=build_dir)
CORS(app)

@app.route('/static/<path:path>')
def send_static(path):
    fpath = os.path.join(build_dir, 'static', path)
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    print fpath
    return flask.send_from_directory(dirname, fname)

@app.route('/')
#@app.route('/<path:path>')
def index(path=''):
    return flask.send_from_directory(build_dir, 'index.html')

@app.route('/api/login', methods=['POST'])
def post_login():
    try:
        username = flask.request.json.get('username', '').encode('utf8')
        password = flask.request.json.get('password', '').encode('utf8')
    except Exception:
        return error('invalid data')
    try:
        user.login(username, password)
        resp = ok()
        resp.set_cookie('session', session.new_session(username))
        return resp
    except user.InvalidAuth as e:
        return error(e.message)

@app.route('/api/logout')
def get_logout():
    if session.del_session():
        return ok()
    else:
        return error('delete session failed')

@app.route('/api/me')
def get_me():
    return ok({'user': session.current_user()})

@app.route('/api/blog', methods=['POST'])
@allow_public_access
def post_blog(session):
    username = session.username
    ct = request.headers.get('Content-Type')
    if ct == 'application/json':
        blog = request.json
    elif ct == 'text/plain':
        blog = {'content': request.data.decode('utf-8')}
    now = datetime.now()
    for k, v in {
        'username': username,
        'title': '',
        'content': '',
        'visible_to': 'everyone',
        'tags': [],
        'ctime': strftime(now),
        'mtime': strftime(now),
    }.items():
        blog.setdefault(k, v)
    db.execute(u'insert into blogs '
               '(username, title, content, json, visible_to, ctime, mtime)'
               ' values (%s,%s,%s,%s,%s,%s,%s)', (
                   blog['username'], blog['title'].encode(config.encoding),
                   blog['content'].encode(config.encoding), json.dumps(blog),
                   blog['visible_to'], blog['ctime'], blog['mtime']
               ))
    blog_id = db.queryone('select last_insert_id()')
    return ok({'id': blog_id})

@app.route('/api/blog')
@app.route('/api/blog/<title>')
def get_blog(title=None):
    blog_id = request.args.get('id')
    username = request.args.get('username')
    str_args = []
    args = []
    if blog_id:
        str_args.append('id = %s')
        args.append(blog_id)
    if title:
        str_args.append('title = %s')
        args.append(title)
    if username:
        str_args.append('username = %s')
        args.append(username)
    querystr = 'select id, json from blogs {} order by ctime desc'.format(
        ' where ' + ','.join(str_args)
    )
    ids_jsons = db.query(querystr, args)
    blogs = []
    for blog_id, blog_json in ids_jsons:
        blog = json.loads(blog_json)
        blog.update(id=blog_id)
        blog['ctime'] = strptime(blog['ctime'])
        blog['mtime'] = strptime(blog['mtime'])
        blogs.append(blog)
    return ok({
        'blogs': blogs,
    })

#@app.route('/', subdomain='<subdomain>')
#def subdomain_dispatch(subdomain):
#    if user.exists(subdomain):
#        return '{}\'s space'.format(subdomain)
#    return 'subdomain: "{}"'.format(subdomain)

@app.after_request
def after_request(response):
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers.add('Access-Control-Allow-Origin',
                             flask.request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.teardown_appcontext
def close_db(err):
    if hasattr(flask.g, 'db'):
        flask.g.db.close()

@app.context_processor
def override_url_for():
    def f_(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.root_path,
                                         endpoint, filename)
                values['q'] = int(os.stat(file_path).st_mtime)
        return flask.url_for(endpoint, **values)
    return dict(url_for=f_)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6561, threaded=True, debug=True)
