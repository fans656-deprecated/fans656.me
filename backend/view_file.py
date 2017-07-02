import flask

import file_util
from util import success_response, error_response
from errors import *


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


def list_root_file_directory():
    return success_response({
        'files': file_util.list_file_directory(u'')
    })


def list_file_directory(dirpath):
    return success_response({
        'files': file_util.list_file_directory(unicode(dirpath))
    })
