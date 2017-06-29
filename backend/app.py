#!/usr/bin/env python
'''
Bugs:
    ) home navigation reload
        when in /blog?page=2 etc, then navigate to "Home"(/home) doesn't reload
    ) pagination input
        can't backspace on page "1"

Deployment:
    ) production deployment should use cache for static files

Functional:
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
import os
import re
import traceback
from datetime import datetime

import flask
from flask import request
from flask_cors import CORS
from dateutil.parser import parse as parse_datetime

import db
import user
import session
import file_util
import utils
import config as conf
from endpoints import endpoints
import errors
from utils import (
    success_response, error_response, require_me_login,
)

app = flask.Flask(__name__, static_folder='')
CORS(app)

for method, path, viewfunc in endpoints:
    viewfunc = utils.handle_exceptions(viewfunc)
    app.route(path, methods=[method])(viewfunc)


@app.route('/api/node/<int:node_id>')
def api_get_node_by_id(node_id):
    try:
        node = query_node_by_id(node_id)
        return success_response({'node': node.to_dict(depth=1)})
    except Exception as e:
        detail = traceback.format_exc(e)
        print detail
        return error_response(detail)


@app.route('/api/node/<ref>')
def get_node_by_ref(ref):
    try:
        node = node_from_ref(ref)
        return success_response({'node': node.to_dict(depth=1)})
    except NotFound:
        return error_response({'detail': 'not found', 'ref': ref})


@app.route('/api/node/<int:node_id>', methods=['DELETE'])
def delete_node(node_id):
    return error_response('currently node delete is not supported')


############################################################# files

@app.route('/api/file/<path:fpath>', methods=['POST'])
@require_me_login
def post_file(fpath):
    isdir = request.args.get('isdir')
    if isdir:
        return success_response()
    else:
        filesize = int(request.headers.get('Content-Length'))
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
    return utils.send_from_directory(conf.FRONTEND_BUILD_DIR, 'static', path)


@app.route('/file/<path:path>')
def get_file(path):
    return utils.send_from_directory(conf.FILES_ROOT, path)


@app.route('/')
@app.route('/<path:path>')
def index(path=''):
    return flask.send_from_directory(conf.FRONTEND_BUILD_DIR, 'index.html')


############################################################# misc


@app.route('/api/backup')
@require_me_login
def backup():
    os.system('./backup.sh')
    return '''
<h1>Backup Finished</h1>
<p>
  See the <a href="https://gitlab.com/fans656/data-fans656.me">data repo</a>
</p>
'''


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


############################################################# echo

#@app.route('/api/echo', methods=['GET', 'POST', 'PUT'])
#def echo():
#    args = request.args
#    content_type = request.headers.get('Content-Type')
#    try:
#        if content_type == 'application/json':
#            data = request.json
#        elif content_type == 'text/plain':
#            data = request.data
#        else:
#            return error_response(
#                'unsupported Content-Type {}'.format(content_type))
#    except Exception:
#        return error_response('malformed data?')
#    return success_response({
#        'args': args,
#        'data': data,
#    })


#@app.route('/', subdomain='<subdomain>')
#def subdomain_dispatch(subdomain):
#    if user.exists(subdomain):
#        return '{}\'s space'.format(subdomain)
#    return 'subdomain: "{}"'.format(subdomain)


if __name__ == '__main__':
    #from gevent.wsgi import WSGIServer
    #server = WSGIServer(('', 6561), app)
    #server.serve_forever()
    app.run(host='0.0.0.0', port=6561, debug=True)
