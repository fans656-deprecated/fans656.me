import os
import sys
import imp
import tempfile

from flask import *

import db


app = Flask(__name__, template_folder='.')


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = '*'
    return r


@app.route('/api/route', methods=['GET'])
def get_route():
    routes = db.get_route()
    return '<pre>{}</pre>'.format(json.dumps({'routes': routes}, indent=2))


@app.route('/api/route', methods=['PUT'])
def put_route():
    content_type = request.headers['content-type']
    if content_type == 'text/plain':
        return handle_create_route_from_script_content(request.data)
    elif content_type == 'application/json':
        return handle_create_route_from_package(request.get_json())
    return 'todo'


@app.route('/', methods=['GET', 'PUT', 'POST', 'DELETE'])
def process_home():
    return handle_request('/')


@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def process_path(path):
    return handle_request('/' + path)


def handle_request(path):
    handler_module = db.get_handler_module(path)
    curdir = os.getcwd()
    try:
        os.chdir(handler_module.working_dir)
        return handler_module.handle(
            request=request,
            db=db,
        )
    finally:
        os.chdir(curdir)


def handle_create_route_from_script_content(script_content):
    fd, fpath = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(script_content)
        handler = imp.load_source('handler', fpath)
        route = handler.route
        if route in sys.modules:
            del sys.modules[route]
        imp.load_source(route, fpath)
        db.create_route_from_script_content(route, script_content)
        return json.dumps({
            'route': route, 'type': 'script', 'data': script_content
        })
    finally:
        os.system('rm ' + fpath + '*')


def handle_create_route_from_package(data):
    route = data['route']
    db.create_route_from_package(route, data['data'])
    return 'ok'


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=3000, threaded=True, debug=True)
    import handler
    print dir(handler)
