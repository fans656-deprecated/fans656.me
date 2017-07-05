import os
import re
import json

import flask

import db
import conf
import user_util
import util
from util import success_response, error_response


def get_read(blog_id):
    args = flask.request.args
    page = int(args.get('page', 1))
    page_size = int(args.get('size', 1000))
    offset = int(args.get('offset', '0'))

    user = user_util.current_user()

    blog = db.query('match (blog:Blog{id: {id}}) return blog', {
        'id': blog_id,
    }, one=True)
    attrs = json.loads(blog['attrs'])

    if not blog:
        return error_response('not found')

    path = blog['path']
    if path.startswith('/'):
        path = path[1:]
    if path.startswith('file'):
        path = path[4:]
    if path.startswith('/'):
        path = path[1:]
    fpath = util.rooted_path(conf.FILES_ROOT, path).encode('utf8')
    text = load_text(fpath, attrs['encoding'])
    if 'search' in args:
        return search_read(text, args['search'])
    content = get_content(text, page, page_size, offset)

    return success_response({
        'content': content,
        'name': attrs['name'],
        'attrs': json.dumps(attrs),
    })


def search_read(text, pattern):
    if not pattern.strip():
        return error_response('invalid pattern')

    offsets = [m.start() for m in re.finditer(pattern, text)]
    more = False
    if len(offsets) > 100:
        offsets = offsets[:100]
        more = True
    return success_response({
        'occurrences': [
            {
                'pattern': pattern,
                'offset': offset,
                'context': text[max(0, offset-100):offset+100],
                'contextOffset': offset - max(0, offset-100),
            } for offset in offsets
        ],
        'more': more,
    })


def load_text(fpath, encoding='utf8'):
    with open(fpath) as f:
        return f.read().decode(encoding, 'ignore')


def get_content(text, page, page_size, offset):
    if offset == 0:
        offset = (page - 1) * page_size
    return text[offset:offset + page_size]
