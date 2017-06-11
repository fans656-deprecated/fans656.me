import os

import flask
from flask_cors import CORS

import session
import user
import utils
from utils import ok, error

build_dir = './frontend/build'

app = flask.Flask(__name__, static_folder=build_dir)
CORS(app)

@app.route('/static/<path:path>')
def send_static(path):
    fpath = os.path.join(build_dir, 'static', path)
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
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
