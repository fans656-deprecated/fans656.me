#!/usr/bin/env python
'''
Bugs:
    ) home navigation reload
        when in /blog?page=2 etc, then navigate to "Home"(/home) doesn't reload
    ) pagination input
        can't backspace on page "1"

Deployment:
    . production deployment should use cache for static files

Functional:
    ) user registration
    ) editor tab in textarea, shift tab to back indent
    ) uploading progress
    ) file explorer
    ) blog/file ref

Presentations:
    ) css var 360 browser compatibility (use less/sass?)
    ) css video mobile width
    ) xiami/video post http => https
    ) code horz scroll

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
from util import (
    success_response, error_response
)

app = flask.Flask(__name__, static_folder='')
CORS(app)

for method, path, viewfunc in endpoints:
    viewfunc = util.handle_exceptions(viewfunc)
    app.route(path, methods=[method])(viewfunc)


@app.route('/api/file/<path:fpath>', methods=['POST'])
def post_file(fpath):
    isdir = flask.request.args.get('isdir')
    if isdir:
        return success_response()
    else:
        filesize = int(flask.request.headers.get('Content-Length'))
        try:
            file_util.save(fpath, filesize)
            return success_response({
                'fpath': fpath,
                'size': filesize,
            })
        except Existed as e:
            return error_response(e.message, Conflict_409)
        except NotAllowed as e:
            return error_response(e.message, Forbidden_403)
        except ServerError as e:
            return error_response(e.message, InternalServerError_500)
        except BadRequest as e:
            return error_response(e.message, BadRequest_400)
        except Exception as e:
            return error_response(e.message)


@app.route('/api/file')
def list_root_file_directory():
    return success_response({
        'files': file_util.list_file_directory('')
    })


@app.route('/api/file/<path:dirpath>')
def list_file_directory(dirpath):
    return success_response({
        'files': file_util.list_file_directory(dirpath)
    })


############################################################# main


@app.route('/static/<path:path>')
def get_static(path):
    return util.send_from_directory(conf.FRONTEND_BUILD_DIR, 'static', path)


@app.route('/file/<path:path>')
def get_file(path):
    return util.send_from_directory(conf.FILES_ROOT, path)


@app.route('/api/<path:path>')
def no_such_api(path):
    return error_response('no such api', 404)


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
    app.run(host='0.0.0.0', port=6561, debug=True)
