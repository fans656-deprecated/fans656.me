import re
import traceback

import flask

import db
from util import success_response, error_response, utcnow, id_from_ctime

def post_blog():
    blog = flask.request.json
    ctime = utcnow()
    params = {
        'content': blog['content'],
        'title': blog.get('title'),
        'tags': blog.get('tags'),
        'ctime': ctime,
        'mtime': ctime,
        'id': id_from_ctime(ctime),
    }
    params = {k: v for k, v in params.items() if v is not None}
    query = (
        'create (n:Blog{{{}}})'.format(
            ', '.join(
                '{key}: {{{key}}}'.format(key=key) for key in params
            )
        )
    )
    db.execute(query, params)
    blog.update(params)
    return success_response()


def get_blogs():
    args = flask.request.args
    page = int(args.get('page', 1))
    size = min(int(args.get('size') or 20), 99999)
    total = db.query_one('match (n:Blog) return count(n)')

    nodes = db.query_nodes(
        'match (n:Blog) return n '
        'order by n.ctime desc '
        'skip {skip} limit {limit}',
        {
            'skip': (page - 1) * size,
            'limit': size,
        }
    )
    # find number of comments
    # TODO: better neo4j query method
    node_id_to_node = {
        node['id']: node for node in nodes
    }
    rows = db.query(
        'match (blog:Blog)-[:has_comment]->(comment:Comment) '
        'return blog.id, count(comment)'
    )['data']
    for blog_id, n_comments in rows:
        if blog_id in node_id_to_node:
            node_id_to_node[blog_id]['n_comments'] = n_comments

    return success_response({
        'blogs': nodes,
        'page': page,
        'size': len(nodes),
        'total': total,
        'n_pages': (total / size) + (1 if total % size else 0),
    })


def get_blog(id):
    blog = db.query_node(
        'match (n:Blog{id: {id}}) return n', {
            'id': id,
        }
    )
    return success_response({
        'blog': blog,
    })


def put_blog(id):
    blog = flask.request.json
    params = {
        'id': id,
        'title': blog.get('title'),
        'content': blog['content'],
        'mtime': utcnow(),
        'tags': blog['tags'],
    }
    params = {k: v for k, v in params.items() if v is not None}
    query = (
        'match (n:Blog{id: {id}}) '
        + 'set {}'.format(', '.join(
            'n.{key} = {{{key}}}'.format(key=key) for key in params
        ))
    )
    db.execute(query , params)
    blog.update(params)
    return success_response({'blog': blog})


def del_blog(id):
    r = db.execute(
        'match (n:Blog{id: {id}}) detach delete n', {
            'id': id,
        }
    )
    assert 'data' in r, 'deletion failed'
    return success_response()


def post_comment(blog_id):
    comment = flask.request.json

    if 'user' in comment:
        username = comment['user']['username']
        is_visitor = False
    else:
        username = comment['visitorName']
        is_visitor = True

    ctime = utcnow()
    db.execute('''
        match (blog:Blog{id: {blog_id}})
        create (comment:Comment{
            username: {username},
            is_visitor: {is_visitor},
            content: {content},
            ctime: {ctime},
            id: {id}
        }),
        (blog)-[:has_comment]->(comment)
        '''
        , {
            'blog_id': blog_id,
            'username': username,
            'is_visitor': is_visitor,
            'content': comment['content'],
            'ctime': ctime,
            'id': id_from_ctime(ctime),
        }
    )
    return success_response()


def get_comments(blog_id):
    comments = db.query_nodes(
        'match (blog:Blog{id: {id}})-[:has_comment]->(comment) '
        'return comment order by comment.ctime asc', {
            'id': blog_id,
        }
    )
    return success_response({
        'comments': comments,
    })
