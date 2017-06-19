import functools

from utils import NotFound

def validate_int(val):
    try:
        int(val)
    except Exception:
        return 'not int'

def validate_str(val):
    assert isinstance(val, str), 'not str'

def validate_unicode(val):
    assert isinstance(val, unicode), 'not unicode'

class Type(object):

    def __init__(self, recipe=None, *args, **kwargs):
        if recipe:
            self.init(recipe, *args, **kwargs)

    def init(self, recipe=None, validate=None):
        self.recipe = recipe
        if isinstance(recipe, type):
            if recipe is int:
                self.validate = make_validator(validate_int)
            elif recipe is str:
                self.validate = make_validator(validate_str)
            elif recipe is unicode:
                self.validate = make_validator(validate_unicode)
            else:
                raise ValueError('todo {}'.format(recipe))
            self.required = True
        elif isinstance(recipe, Type):
            self.__dict__.update(recipe.__dict__)
        elif isinstance(recipe, list) and len(recipe) == 1:
            assert isinstance(recipe, Type)
            self.__dict__.update(ListType(recipe))
            return
        else:
            raise ValueError('todo {}'.format(recipe))
        if validate:
            self.validate = make_validator(validate)

    def __repr__(self):
        return 'Type({})'.format(self.recipe)

    def __or__(self, o):
        return OrType(self, o)

class OrType(Type):

    def __init__(self, type1, type2):
        self.recipe = [type1.recipe, type2.recipe]
        self.type1 = type1
        self.type2 = type2
        self.required = type1.required or type2.required

    def validate(self, val):
        err1 = self.type1.validate(val)
        err2 = self.type2.validate(val)
        if not err1 or not err2:
            return None
        return err1 or err2

class ListType(Type):

    def __init__(self, type_):
        self.recipe = type_.recipe
        self.type = type_

    def validate(self, a):
        if not isinstance(a, list):
            return 'not list'
        errors = [self.type.validate(t) for t in a]
        return errors

def make_validator(validate):
    @functools.wraps(validate)
    def validate_(val):
        try:
            r = validate(val)
        except Exception as e:
            return e.message or 'invalid'
        if isinstance(r, bool):
            return None if r else 'invalid'
        else:
            return r
    return validate_

def params(schema):
    def deco(f):
        @functools.wraps(f)
        def f_(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except NotFound as e:
                return error(e.message, 404)
            except AssertionError as e:
                return error(e.message, 400)
        return f_
    return deco

def make_schema(recipe):
    for name, type_or_schema in recipe.items():
        if isinstance(type_or_schema, dict):
            recipe[name] = make_schema(type_or_schema)
        elif isinstance(type_or_schema, Type):
            pass
        else:
            recipe[name] = Type(type_or_schema)
    return recipe

class Validator(object):

    def __init__(self, schema_recipe):
        self.schema = make_schema(schema_recipe)

    def validate(self, params):
        errors = get_validation_errors(self.schema, params)
        return errors

    __call__ = validate

def get_validation_errors(schema, params, errors=None):
    errors = errors or {}
    for name, param_type in schema.items():
        if param_type.required and name not in params:
            errors[name] = {'error': 'missing', 'type': param_type}
            continue
        val = params[name]
        error = param_type.validate(val)
        if error:
            errors[name] = {'error': error, 'type': param_type}
    return errors

def range_validator(lo=None, hi=None):
    def validate_range(val):
        if lo is not None and val < lo:
            return 'too small'
        if hi is not None and hi < val:
            return 'too large'
    return validate_range

Int = Type(int)
Str = Type(str)
Unicode = Type(unicode)
String = Str | Unicode

Link = Type()

Node = Type({
    'data': String,
    'links': [Link],
})

Link.init({
    'rel': String,
    'dst': Int | String | Node,
})

if __name__ == '__main__':
    pass
    #v = Validator({
    #    'foo': String,
    #})

    #print v({
    #    'foo': '3'
    #})
