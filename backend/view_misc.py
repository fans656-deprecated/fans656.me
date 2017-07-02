import json

import flask
from f6 import each

import db
import conf
import util
from util import success_response, error_response


def get_static(path):
    return util.send_from_directory(conf.FRONTEND_BUILD_DIR, 'static', path)


def get_file(path):
    return util.send_from_directory(conf.FILES_ROOT, path)


def no_such_api(path):
    return error_response('no such api', 404)


def get_custom_url(path):
    if not path:
        return error_response('invalid path')
    node = db.query(
        'match (n) where n.custom_url = {path} return n', {
            'path': '/' + path
        }, one=True)
    if not node:
        return error_response('Oops, not found', 404)
    labels = node['meta']['labels']
    if 'Blog' in labels:
        return success_response({
            'type': 'blog',
            'blog': node,
        })
    else:
        return success_response({
            'type': 'unknown',
            'detail': json.dumps(node, indent=2)
        })
