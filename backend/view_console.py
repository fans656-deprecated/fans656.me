import re
import traceback

import flask

import db
from view_blog import query_blogs
import user_util
import util
from util import success_response, error_response, utcnow, new_node_id

def post_cmd():
    data = flask.request.json
    if not data:
        return error_response('invalid POST body')
    cmd = data.get('cmd')
    if not cmd:
        return error_response('empty cmd')
    url = data.get('url')
    if not url:
        return error_response('unknown context (url)')

    page = 1
    size = 20

    # search tags
    blogs, total = query_blogs('''
        match (blog:Blog)-[:has_tag]->(tag:Tag)
        where tag.content contains {search_tags__tag}
    ''', {
        'search_tags__tag': cmd
    }, page=page, size=size)
    if not blogs:
        return error_response('no blogs tagged "{}"'.format(cmd))
    return success_response({
        'blogs': blogs,
        'page': page,
        'size': len(blogs),
        'total': total,
        'n_pages': (total / size) + (1 if total % size else 0),

        'tag': blogs
    })
