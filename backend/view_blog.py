import re
import itertools
import traceback

import flask
from f6 import each

import db
import user_util
import util
from util import success_response, error_response, utcnow, new_node_id

@user_util.require_me_login
def post_blog():
    blog = flask.request.json
    ctime = utcnow()
    tags = blog.get('tags', [])
    print blog

    blog_id = new_node_id()
    params = {
        'content': blog['content'],
        'title': blog.get('title'),
        'ctime': ctime,
        'mtime': ctime,
        'id': blog_id,
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
    update_tags(blog)

    return success_response()


def get_blogs():
    args = flask.request.args
    tags = filter(bool, util.parse_query_string(args.get('tags', [])))
    page = int(args.get('page', 1))
    size = min(int(args.get('size') or 20), 999)

    if tags:
        return response_blogs_by_tags(tags, page=page, size=size)
    else:
        blogs, total = query_blogs(page=page, size=size)
        return success_response({
            'blogs': blogs,
            'pagination': make_pagination(blogs, page, size, total),
        })


def get_blog(id):
    query = (
        'match (blog:Blog{id: {id}}) where True '
        + get_blog_mandatory_preds()
        + 'return blog'
    )
    blog = db.query(query, {
        'id': id,
    }, one=True)
    if not blog:
        return error_response('not found', 403)
    blog['tags'] = tags_by_blog_id(id)
    return success_response({
        'blog': blog,
    })


@user_util.require_me_login
def put_blog(id):
    blog = flask.request.json
    params = {
        'id': id,
        'title': blog.get('title'),
        'content': blog['content'],
        'mtime': utcnow(),
    }

    custom_url = blog.get('custom_url')
    if custom_url:
        params['custom_url'] = blog['custom_url']

    params = {k: v for k, v in params.items() if v is not None}
    query = (
        'match (n:Blog{id: {id}}) '
        + 'set {}'.format(', '.join(
            'n.{key} = {{{key}}}'.format(key=key) for key in params
        ))
    )
    db.execute(query , params)
    update_tags(blog)
    blog.update(params)
    return success_response({'blog': blog})


@user_util.require_me_login
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
            'id': new_node_id(),
        }
    )
    return success_response()


def get_comments(blog_id):
    comments = db.query(
        'match (blog:Blog{id: {id}})-[:has_comment]->(comment) '
        'return comment order by comment.ctime asc', {
            'id': blog_id,
        }, cols=1)
    return success_response({
        'comments': comments,
    })


@user_util.require_me_login
def delete_comments(comment_id):
    r = db.execute(
        'match (comment:Comment{id: {id}}) detach delete comment', {
            'id': comment_id,
        }
    )
    if 'data' not in r:
        return error_response('not found', 404)
    return success_response()


def search():
    args = flask.request.json

    by = args['by']
    match = args['match']

    if by == 'tags' and match == 'partial':
        return response_blogs_by_tags(args.get('tags', []))
    return error_response('unsupported by={}'.format(data['by']))


def tags_by_blog_id(id):
    tags = db.query(
        'match (:Blog{id: {id}})-[rel:has_tag]->(tag) '
        'return tag.content order by rel.index asc', {
            'id': id,
        }, cols=1)
    return tags


def update_tags(blog):
    tags = blog.get('tags', [])
    db.query('match (blog:Blog{id: {id}})-[rel:has_tag]->(tag) '
             'delete rel', {
                 'id': blog['id'],
             })
    for i, tag in enumerate(tags):
        # TODO: silly implementation
        tag_exists = db.query(
            'match (tag:Tag{content: {tag}}) return count(tag)', {
                'tag': tag,
            }, one=True)
        if not tag_exists:
            db.query('create (tag:Tag{content: {tag}, id: {tag}})', {
                'tag': tag,
            })
        db.query(
            'match (blog:Blog{id: {blog_id}}), (tag:Tag{id: {tag_id}})'
            'create (blog)-[:has_tag{index: {index}}]->(tag)', {
                'blog_id': blog['id'],
                'tag_id': tag,
                'index': i,
            })


def response_blogs_by_tags(tags, page=1, size=20):
    blogs, total = query_blogs('''
        match (blog:Blog)-[:has_tag]->(tag:Tag)
        where any(
            partial_tag in {search__partial_tags}
            where tag.content contains partial_tag
        )
    ''', {
        'search__partial_tags': tags
    }, page=page, size=size)

    tags = list(set(itertools.chain(*each(blogs)['tags'])))

    return success_response({
        'blogs': blogs or [],
        'pagination': {
            'page': page,
            'size': len(blogs),
            'total': total,
            'nPages': (total / size) + (1 if total % size else 0),
        },
        'tags': tags,
    })


def query_blogs(preds='', params=None, page=1, size=20):
    params = params or {}

    stmt = '''
        match (blog:Blog) where true
    ''' + get_blog_mandatory_preds() + ' ' + preds

    total_stmt = stmt + ' return count(distinct blog)'
    #print '=' * 40, 'total_stmt'
    #print total_stmt
    #raw_input()
    total = db.query(total_stmt, params, one=True)

    params.update({
        'skip': (page - 1) * size,
        'limit': size,
    })
    blogs_stmt = stmt + '''
        return distinct blog
        order by blog.ctime desc
        skip {skip} limit {limit}
    '''
    #print '=' * 40, 'blogs_stmt'
    #print blogs_stmt
    #raw_input()
    blogs = db.query(blogs_stmt, params, cols=1)

    attach_num_comments_to_blogs(blogs)
    attach_tags_to_blogs(blogs)
    return blogs, total


def get_blog_mandatory_preds():
    try:
        user = user_util.current_user()
    except RuntimeError:
        user = {'username': 'fans656'}
    username = user and user.get('username', None)

    preds = ''
    if username != 'fans656':
        preds += ('''
            and not ((blog)-[:has_tag]->(:Tag{content: '..'}))
            and not ((blog)-[:has_tag]->(:Tag{content: '.'}))
                  ''')
    return preds


def attach_num_comments_to_blogs(blogs):
    id_to_blog = {
        blog['id']: blog for blog in blogs
    }
    rows = db.query(
        'match (blog:Blog)-[:has_comment]->(comment:Comment) '
        'return blog.id, count(comment)'
    )
    for blog_id, n_comments in rows:
        if blog_id in id_to_blog:
            id_to_blog[blog_id]['n_comments'] = n_comments


def attach_tags_to_blogs(blogs):
    for blog in blogs:
        blog['tags'] = tags_by_blog_id(blog['id'])


def make_pagination(blogs, page, size, total):
    return {
        'page': page,
        'size': len(blogs),
        'total': total,
        'nPages': (total / size) + (1 if total % size else 0),
    }


if __name__ == '__main__':
    from pprint import pprint
