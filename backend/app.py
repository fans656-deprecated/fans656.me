#!/usr/bin/env python
'''
Bugs:
    . home navigation reload
        when in /blog?page=2 etc, then navigate to "Home"(/home) doesn't reload
    ) pagination input
        can't backspace on page "1"

Priorities:
    ) custom url
    ) gallery (jobs/girls)
    ) movie
    ) music
    ) secret blog
    ) mobile nav
    ) blog edit autosave

Console:
    ) input tab sequence
    . pagination
    ) help prompt

Important:
    . require_me_login
        require authorization to edit
    . tags and meta-tags
        such as only-me blogs (write something private)
    ) mobile nav
        entry point for "Resume" etc
    . single blog view

Deployment:
    . production deployment should use cache for static files

Functional:
    ) search by tags
    . user registration
    ) editor tab in textarea, shift tab to back indent
    ) uploading progress
    ) file explorer

Presentations:
    ) css var 360 browser compatibility (use less/sass?)
    . css video mobile width
    . xiami/video post http => https
    . code horz scroll

Apps:
    ) TODO page
        add todos, categoried by tags (long term, short term...)
        version control
    ) txt reader
'''

import flask
from flask_cors import CORS

import file_util
import conf
from endpoints import endpoints
import util
from util import success_response, error_response

app = flask.Flask(__name__, static_folder='')
CORS(app)

for method, path, viewfunc in endpoints:
    viewfunc = util.handle_exceptions(viewfunc)
    app.route(path, methods=[method])(viewfunc)


@app.route('/')
@app.route('/<path:path>')
def index(path=''):
    return flask.send_from_directory(conf.FRONTEND_BUILD_DIR, 'index.html')


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


if __name__ == '__main__':
    #from gevent.wsgi import WSGIServer
    #server = WSGIServer(('', 6561), app)
    #server.serve_forever()
    app.run(host='0.0.0.0', port=4430, threaded=True)
