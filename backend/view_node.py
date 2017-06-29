import re
import traceback

from flask import request

import db
from util import success_response, error_response

def get_nodes():
    """Get node list

    example:

        GET /api/node?label=blog&page=2&size=50
    """
    args = request.args
    label = args.get('label', '')
    page = int(args.get('page', 1))
    size = min(int(args.get('size') or 20), 99999)
    try:
        label = ':' + label if label else ''
        query = '''
            match (n{}) return n
            order by n.ctime desc skip {{skip}} limit {{limit}}
        '''.format(label)
        r = db.cypher(query, {
                'skip': (page - 1) * size,
                'limit': size,
            }
        )
        data = r['data']
        for d in data:
            d[0]['data']['id'] = d[0]['metadata']['id']
        print data[19][0]['data']
        total = db.cypher(
            'match (n{}) return count(n)'.format(label))['data'][0][0]
        return success_response({
            'nodes': [d[0]['data'] for d in data],
            'page': page,
            'size': len(data),
            'total': total,
            'nPages': (total / size) + (1 if total % size else 0),
        })
    except Exception as e:
        return error_response(e)
    rels = {}
    for rel in args:
        m = re.match(r'rels\[(\w+)\]', rel)
        if m:
            rels[m.group(1)] = args.get(rel)
    try:
        data = node.query_by_rels(rels=rels, page=page, size=size)
    except Exception as e:
        detail = traceback.format_exc(e)
        print detail
        return error_response(detail)
    return success_response({
        'nodes': [n.to_dict(depth=1) for n in data.nodes],
        'page': data.page,
        'size': data.size,
        'total': data.total,
        'nPages': (data.total / size) + (1 if data.total % size else 0),
    })


def post_node():
    try:
        literal = request.json
        node = Node.from_literal(literal)
        node.graph.dump()
    except Exception as e:
        detail = traceback.format_exc(e)
        print detail
        return error_response(detail)
    print 'posted', node.data[:20], datetime.now()
    return success_response({'node': node.to_dict()})


def put_node(node_id):
    old_node = query_node_by_id(node_id)
    if not old_node:
        return error_response('no node with id = {}'.format(node_id))
    try:
        new_node = Node.from_literal(request.json)
        old_node.data = new_node.data
        return success_response({'node': new_node.to_dict()})
        new_node.graph.dump()
        return success_response({'node': new_node.to_dict()})
    except Exception as e:
        return error_response(utils.indented_exception(e))
