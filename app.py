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
from node import Blog

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

@app.route('/api/node', methods=['POST'])
def post_node():
    args = request.json
    if not args:
        return error('args required')
    node_type = args.get('type')
    if not node_type:
        return error('arg `type` required')
    if node_type == 'blog':
        content = args.get('content')
        if not content:
            return error('content required')
        blog = Blog(content, title=args.get('title'), tags=args.get('tags'))
        with db.getdb() as c:
            blog.persist(c)
        return ok({
            'blog': dict(blog)
        })
    elif node_type == 'image':
        return error('todo image node')
    else:
        return error('unrecognized node type: {}'.format(node_type))

@app.route('/api/node', methods=['PUT'])
def put_node():
    pass

@app.route('/api/blog')
def get_blog():
    with getdb() as c:
        c.execute('select s')

@app.route('/api/node/<id>')
def get_node():
    pass

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
