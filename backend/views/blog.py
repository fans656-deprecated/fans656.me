import re
import traceback

import flask

import db2 as db
from utils import success_response, error_response, utcnow

def post_blog():
    blog = flask.request.json
    return success_response({
        'blog': blog
    })


def get_blogs():
    """Get blog list

    example:

        GET /api/blog?page=2&size=50
    """
    print 'get_blogs'
    args = flask.request.args
    page = int(args.get('page', 1))
    size = min(int(args.get('size') or 20), 99999)
    total = db.cypher('match (n:Blog) return count(n)')['data'][0][0]

    r = db.cypher(
        'match (n:Blog) return n '
        'order by n.ctime desc '
        'skip {skip} limit {limit}',
        {
            'skip': (page - 1) * size,
            'limit': size,
        }
    )
    data = r['data']
    for d in data:
        d[0]['data']['id'] = d[0]['metadata']['id']

    return success_response({
        'blogs': [d[0]['data'] for d in data],
        'page': page,
        'size': len(data),
        'total': total,
        'n_pages': (total / size) + (1 if total % size else 0),
    })


def get_blog(node_id):
    blog = db.queryone(
        'match (n:Blog) where id(n) = {} return n'.format(node_id)
    )
    return success_response({
        'blog': blog,
    })


def put_blog(node_id):
    blog = flask.request.json
    params = {
        'id': node_id,
        'title': blog.get('title'),
        'content': blog['content'],
        'mtime': utcnow(),
        'tags': blog['tags'],
    }
    params = {k: v for k, v in params.items() if v is not None}
    query = (
        'match (n:Blog) where id(n) = {id} '
        + 'set {}'.format(', '.join(
            'n.{key} = {{{key}}}'.format(key=key) for key in params
        ))
    )
    db.execute(query , params)
    blog.update(params)
    return success_response({'blog': blog})
