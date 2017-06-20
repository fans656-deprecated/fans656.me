import functools
import traceback

from node import Node, query
from utils import Response, NotFound

class Type(object):

    def __init__(self, coerce=None, optional=None, default=None):
        self.coerce_func = coerce
        if default is not None and optional is None:
            optional = True
        self.default = default
        self.optional = optional
        self.required = not optional

    def convert(self, val):
        if val is None:
            default = self.default
            if callable(default):
                val = default()
            else:
                val = default
        if self.coerce_func:
            val = self.coerce_func(val)
        return val

    def __call__(self, *args, **kwargs):
        if args:
            assert len(args) == 1, 'only one value is allowed'
            assert not kwargs, 'no keyword arguments is allowed'
            val = args[0]
            return self.validate_and_convert(val)
        else:
            assert not args, 'must use keyword arguments'
            return self.__class__(*args, **kwargs)

    def validate_and_convert(self, val):
        error = self.validate(val)
        if error:
            raise ConversionError(error)
        return self.convert(val)

    def __or__(self, o):
        if isinstance(o, OrType):
            return o | self
        else:
            return OrType(self, o)

Anything = Type

def report_type(name):
    def deco(f):
        @functools.wraps(f)
        def f_(*args, **kwargs):
            error = f(*args, **kwargs)
            if error:
                error.update({'type': name})
            return error
        return f_
    return deco

class IntegerType(Type):

    def __init__(self, min=None, max=None, default=0, *args, **kwargs):
        super(IntegerType, self).__init__(*args, **kwargs)
        self.min = min
        self.max = max
        self.default = default

    @report_type('Integer')
    def validate(self, val):
        if self.coerce_func:
            try:
                self.coerce_func(val)
            except Exception as e:
                return {'error': 'coerce failed', 'value': val,
                        'reason': str(e)}
        try:
            val = int(val)
        except ValueError, TypeError:
            return {'error': 'bad value', 'value': val}
        if self.min is not None and self.min <= val:
            return {'error': 'bad value', 'reason': 'too small'}
        if self.max is not None and val <= self.max:
            return {'error': 'bad value', 'reason': 'too large'}

class FloatType(Type):

    def __init__(self, min=None, max=None, default=0.0, *args, **kwargs):
        super(FloatType, self).__init__(*args, **kwargs)
        self.min = min
        self.max = max
        self.default = default

    # TODO: validate

class StringType(Type):

    def __init__(self, encoding='utf-8', *args, **kwargs):
        super(StringType, self).__init__(*args, **kwargs)
        self.encoding = encoding
        if not self.coerce_func:
            self.coerce_func = unicode

    @report_type('String')
    def validate(self, val):
        if isinstance(val, str):
            try:
                val.encode(self.encoding)
            except UnicodeDecodeError:
                return {'error': 'bad value', 'value': val}
        elif isinstance(val, unicode):
            return
        else:
            return {'error': 'bad value', 'value': val}

    def convert(self, val):
        if not isinstance(val, unicode):
            val = val.decode(self.encoding)
        return super(StringType, self).convert(val)

class OrType(Type):

    def __init__(self, *types):
        self.types = list(types)
        self.optional = any(tp.optional for tp in types)
        self.required = not self.optional

    def validate(self, val):
        if val is None and self.optional:
            return
        errors = [type.validate(val) for type in self.types]
        if any(error is None for error in errors):
            return None
        return {'error': 'bad value', 'possible_reasons': errors}

    def convert(self, val):
        errors = []
        for type in self.types:
            error = type.validate(val)
            if error:
                errors.append(error)
                continue
            try:
                return type.convert(val)
            except Exception as e:
                reason = traceback.format_exc()
                errors.append({'error': 'conversion failed', 'reason': reason})
                continue
        raise ConversionError(errors)

    def __or__(self, o):
        ret = OrType()
        ret.types = self.types + get_or_types(o)
        return ret

class ListType(Type):

    def __init__(self, type=Anything, *args, **kwargs):
        super(ListType, self).__init__(*args, **kwargs)
        self.type = type

    def validate(self, a):
        errors = filter(bool, map(self.type.validate, a))
        if errors:
            return {'error': 'bad value', 'reason': errors}
        else:
            return None

    def convert(self, a):
        a = super(ListType, self).convert(a)
        return map(self.type.convert, a)

    def __call__(self, *args, **kwargs):
        return ListType(*args, **kwargs)

class Dict(Type):

    def __init__(self, name_to_type, *args, **kwargs):
        self.update(name_to_type, *args, **kwargs)

    def validate(self, params):
        errors = []
        if not isinstance(params, dict):
            errors.append({'error': 'bad value', 'value': params})
            return errors
        for name, type in self:
            # check missing param
            if type.required:
                if name not in params:
                    errors.append({'error': 'missing', 'name': name})
                    continue
            elif name not in params:
                continue
            # validate value
            if name in params:
                error = type.validate(params[name])
                if error:
                    error.update({'name': name})
                    errors.append(error)
        return errors or None

    def convert(self, params):
        ret = {name: type.convert(params.get(name)) for name, type in self}
        return super(Dict, self).convert(ret)

    def __iter__(self):
        return iter(self.name_to_type.items())

    def update(self, name_to_type, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        self.name_to_type = name_to_type

schema = Dict

def get_or_types(tp):
    if isinstance(tp, OrType):
        return tp.types
    else:
        return [tp]

class ConversionError(Exception):

    def __init__(self, error):
        super(ConversionError, self).__init__(str(error))
        self.error = error

String = StringType()
Integer = IntegerType()
Float = FloatType()
List = ListType()

##################################################### node related

class ThisNode(object):

    pass

def node_from_id(node_id):
    if node_id == 0:
        return ThisNode()
    else:
        return Node(node_id)

def node_from_ref(ref):
    nodes = query(ref=ref)
    if not nodes:
        raise NotFound('no node with ref={}'.format(ref))
    elif len(nodes) == 1:
        return nodes[0]
    else:
        raise Response({
            'detail': 'multiple nodes with ref={} are found'.format(ref),
            'ids': [node.id for node in nodes]
        })

def node_from_literal(literal):
    node = Node(literal['data'])
    links = literal['links']
    for link in links:
        rel = link['rel']
        dst = link['dst']
        if isinstance(dst, ThisNode):
            dst = node
        node.link(rel, dst)
    return node

Link = Dict({})

NodeLiteral = Dict({
    'data': String,
    'links': List(Link, default=lambda: []),
}, coerce=node_from_literal)

Link.update({
    'rel': String,
    'dst': (
        String(coerce=node_from_ref)
        | Integer(coerce=node_from_id)
        | NodeLiteral
    ),
})

if __name__ == '__main__':

    class Node(object):

        def __init__(self, what):
            self.what = what

        def __repr__(self):
            return 'Node({})'.format(repr(self.what))

    def node_from_ref(ref):
        return Node(ref)

    def node_from_id(id):
        return Node(id)

    Link = Dict({
        'rel': String,
        'dst': String(coerce=node_from_ref) | Integer(coerce=node_from_id),
    })
    PostNode = Dict({
        'data': String,
        'links': List(Link, default=lambda: []),
    })
    o = {
        u'data': u'foo',
        u'links': [
            {'rel': 'foo', 'dst': 'foo'},
            {'rel': 'type', 'dst': 1}
        ]
    }
    print Dict({
        'data': String,
        'links': List(Link, default=lambda: []),
    })({
        u'data': u'foo',
        u'links': [
            {'rel': 'foo', 'dst': 'foo'},
            {'rel': 'type', 'dst': 1}
        ]
    })
