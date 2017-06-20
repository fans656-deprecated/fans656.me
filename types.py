class Type(object):

    def __init__(self, coerce=None, optional=False):
        self.coerce_func = coerce
        self.optional = optional

    def __call__(self, *args, **kwargs):
        if args:
            assert len(args) == 1, 'only one value is allowed'
            assert not kwargs, 'no keyword arguments is allowed'
            val = args[0]
            self.convert(val)
        else:
            assert not args, 'must use keyword arguments'
            return self.__class__(*args, **kwargs)

    def __or__(self, o):
        if isinstance(o, OrType):
            return o | self
        else:
            return OrType(self, o)

Anything = Type

class IntegerType(Type):

    def __init__(self, min=None, max=None, default=0, *args, **kwargs):
        super(IntegerType, self).__init__(*args, **kwargs)
        self.min = min
        self.max = max
        self.default = default

    def convert(self, val):
        if val is None:
            return self.default
        if self.coerce_func:
            val = self.coerce_func(val)
        if self.min is not None:
            assert self.min <= val, 'too small'
        if self.max is not None:
            assert val <= self.max, 'too large'
        return val

class FloatType(Type):

    def __init__(self, min=None, max=None, default=0.0, *args, **kwargs):
        super(FloatType, self).__init__(*args, **kwargs)
        self.min = min
        self.max = max
        self.default = default

class StringType(Type):

    def __init__(self, encoding='utf-8', *args, **kwargs):
        super(StringType, self).__init__(*args, **kwargs)
        self.encoding = encoding
        if not self.coerce_func:
            self.coerce_func = unicode

    def convert(self, val):
        if not self.optional and val is None:
            raise Missing()
        return self.coerce_func(val)

class OrType(Type):

    def __init__(self, *types):
        self.types = list(types)
        self.optional = any(tp.optional for tp in types)

    def convert(self, val):
        for type in self.types:
            try:
                return type.convert(val)
            except Exception:
                continue
        else:
            assert False, 'bad value'

    def __or__(self, o):
        ret = OrType()
        ret.types = self.types + get_or_types(o)
        return ret

class ListType(Type):

    def __init__(self, type=Anything):
        self.type = type

class StructType(Type):

    def __init__(self, name_to_type):
        self.name_to_type = name_to_type

    def validate(self, params):
        errors = []
        if not isinstance(params, dict):
            errors.append('bad value {}'.format(params))
            return errors
        for name, type in self:
            if not type.optional and name not in params:
                errors.append('missing {}'.format(name))
                continue
            # TODO: validate value
        return errors or None

    def __iter__(self):
        return iter(self.name_to_type.items())

def get_or_types(tp):
    if isinstance(tp, OrType):
        return tp.types
    else:
        return [tp]

class Missing(Exception): pass

String = StringType()
Integer = IntegerType()
Float = FloatType()
List = ListType()

if __name__ == '__main__':

    class Node(object):

        def __init__(self, what):
            self.what = what

    def node_from_ref(ref):
        return Node(ref)

    def node_from_id(id):
        return Node(id)

    Link = StructType({
        'rel': String,
        'dst': String(coerce=node_from_ref) | Integer(coerce=node_from_id),
    })
    print Link.validate({'rel': None, 'dst': None})
