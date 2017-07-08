import os

import flask
from PIL import Image

import conf
import util
from util import success_response, error_response


def get_gallery():
    data = flask.request.json

    srcs = []

    files = [f.encode('utf8') for f in data['files']]
    for path in files:
        srcs.append(os.path.join('/file', path))

    paths = [f.encode('utf8') for f in data['paths']]
    for path in paths:
        dirpath = util.rooted_path(conf.FILES_ROOT, path)
        srcs.extend(os.path.join('/file', path, fname)
                    for fname in sorted(os.listdir(dirpath))
                    if not fname.startswith('tmp-'))

    return success_response({
        'srcs': srcs,
    })
