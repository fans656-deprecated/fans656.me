import functools
from copy import copy

from flask import request

from utils import error_response

def api(method, url, schema):
    def deco(f):
        @functools.wraps(f)
        def f_(*args, **kwargs):
            params = get_params(method)
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

class Type(object):

    def __init__(self):
        pass

def normalize(recipe):
    if isinstance(recipe, str):
        if recipe == 'string':
            return {'type': 'string'}
        elif recipe == 'integer':
            return {'type': 'integer'}
        else:
            raise Exception(recipe)
    elif isinstance(recipe, list):
        return {'type': 'list', 'contained_type': recipe[0]}
    elif isinstance(recipe, tuple):
        return {'type': 'or', 'types': recipe}
    elif isinstance(recipe, dict):
        return {'type': 'struct', 'types': recipe}
    else:
        raise Exception('unknown recipe')

def to_type(recipe):
    recipe = normalize(recipe)
    type_cls = {
        'string': StringType,
        'integer': IntegerType,
        'struct': StructType,
        'list': ListType,
        'or': OrType,
    }[recipe['type']]
    return type_cls(recipe)

class StructType(Type):

    def __init__(self, recipe):
        print recipe.items()
        self.name_to_type = {name: to_type(type_recipe)
                             for name, type_recipe in recipe.items()}

class ListType(Type):

    def __init__(self, recipe):
        self.contained_type = to_type(recipe['contained_type'])

class IntegerType(object):

    def __init__(self, recipe):
        pass

class StringType(object):

    def __init__(self, recipe):
        pass

class OrType(object):

    def __init__(self, recipe):
        self.types = map(to_type, recipe['types'])

Schema = StructType

if __name__ == '__main__':
    schema = {
        'data': 'string',
        'links': [{
            'rel': 'string',
            #'dst': (
            #    {'type': 'integer', 'coerce': 'node_from_id'},
            #    {'type': 'string',  'coerce': 'node_from_ref'},
            #)
        }],
    }
    schema = Schema(schema)
    print schema
