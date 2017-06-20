import functools

from flask import request

from paramtypes import Dict, ConversionError
from utils import error_response, Response

def api(method, url, schema, **comments):
    if isinstance(schema, dict):
        schema = Dict(schema)
    def deco(f):
        @functools.wraps(f)
        def f_(*args, **kwargs):
            params = get_params(method)
            try:
                params = schema.validate_and_convert(params)
            except ConversionError as e:
                print 'ConversionError', e.error
                return error_response(e.error)
            except Response as e:
                return error_response(e.data)
            except Exception as e:
                return error_response(str(e), 500)
            if schema.coerce_func:
                return f(params, *args, **kwargs)
            else:
                kwargs.update(params)
                return f(*args, **kwargs)
        return flask_app.route(url, methods=[method])(f_)
    return deco

def get_params(method):
    if method in ('GET', 'DELETE'):
        return request.args
    elif method in ('POST', 'PUT'):
        return request.json
    else:
        raise ValueError('unsupported method {}'.format(method))

flask_app = None

def API(app):
    global flask_app
    flask_app = app
