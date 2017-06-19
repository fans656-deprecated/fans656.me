import functools

from utils import NotFound

def make_type(recipe, *args, **kwargs):
    if is_builtin_type(recipe):
        return from_builtin_type(recipe, *args, **kwargs)
    elif is_schema(recipe):
        return ParamsType(recipe)
    elif is_list_type(recipe):
        return ListType(recipe)
    elif isinstance(recipe, Type):
        return recipe
    else:
        raise ValueError('make_type: unknown recipe {}'.format(recipe))

def is_builtin_type(tp):
    return isinstance(tp, type)

def is_schema(sch):
    return isinstance(sch, dict)

def is_list_type(l):
    return isinstance(l, list) and len(l) == 1

def from_builtin_type(tp):
    if tp is int:
        return IntType(tp)
    elif tp is str:
        return StrType(tp)
    elif tp is unicode:
        return UnicodeType(tp)
    else:
        raise ValueError('TODO from_builtin_type {}'.format(tp))

class Type(object):

    def __init__(self, recipe):
        self.recipe = recipe

    def __repr__(self):
        return self.__class__.__name__

class ParamsType(object):

    def __init__(self, recipe):
        self.params = {
            name: make_type(type_recipe)
            for name, type_recipe in recipe.items()
        }

    def validate(self, params):
        if not isinstance(params, dict):
            raise ValueError(
                'ParamsType.validate expect `dict`, got {}'.format(params))
        errors = []
        for name, type_ in self.params.items():
            if name not in params:
                errors.append({'name': name,
                               'error': 'missing',
                               'type': type_.__class__.__name__,
                               'value': None,
                               })
                continue
            val = params[name]
            error = type_.validate(val)
            if error:
                error.update({'name': name})
                errors.append(error)
        return errors or None

class IntType(Type):

    def validate(self, val):
        try:
            int(val)
        except Exception:
            return {'error': 'bad value',
                    'value': val,
                    'type': self.__class__.__name__
                    }

### exceptions

class Missing(Exception):

    def __init__(self, name, type_):
        super(Missing, self).__init__('missing {}'.format(name))
        self.type = type_

class BadValue(Exception):

    def __init__(self, value):
        self.value = value

#########################################################

if __name__ == '__main__':
    # IntType
    tp = make_type(int)
    assert isinstance(tp, IntType)
    assert tp.validate(3) is None
    err = tp.validate('foo')
    assert err is not None

    # ParamsType
    tp = make_type({})
    assert isinstance(tp, ParamsType)
    for val in (3, 'foo'):
        try:
            assert tp.validate(val) is None
        except ValueError:
            pass

    tp = make_type({'foo': int})
    assert isinstance(tp, ParamsType)
    err = tp.validate({})
    assert len(err) == 1
    assert err[0]['error'] == 'missing'
    print err
    #assert 'missing' in err['foo']
    err = tp.validate({'foo': 'hi', 'bar': None})
    assert err
    print err
