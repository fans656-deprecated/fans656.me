import re
import traceback

import flask

import db
import user_util
import util
from util import success_response, error_response, utcnow, new_node_id

@user_util.require_me_login
def post_blog():
    blog = flask.request.json
    ctime = utcnow()
    tags = blog.get('tags', [])

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
    update_tags(blog, tags)

    blog.update(params)
    return success_response()


def get_blogs():
    args = flask.request.args
    tags = util.parse_query_string(args.get('tags'))
    page = int(args.get('page', 1))
    size = min(int(args.get('size') or 20), 99999)
    total = db.query('match (n:Blog) return count(n)', one=True)

    # TODO: filter by tags is ugly & difficult to implement
    # when tags are array property of Blog
    # do it using relationships
    stmt = '''
        match (blog:Blog) where true
    ''' + get_blog_preds() +  '''
        return blog
        order by blog.ctime desc
        skip {skip} limit {limit}
    '''
    print stmt
    blogs = db.query(stmt, {
            'skip': (page - 1) * size,
            'limit': size,
        }, cols=1)
    # find number of comments
    # TODO: better neo4j query method
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

    # get tags
    for blog in blogs:
        blog['tags'] = tags_by_blog_id(blog['id'])

    return success_response({
        'blogs': blogs,
        'page': page,
        'size': len(blogs),
        'total': total,
        'n_pages': (total / size) + (1 if total % size else 0),
    })


def get_blog(id):
    query = (
        'match (blog:Blog{id: {id}}) where True '
        + get_blog_preds()
        + 'return blog'
    )
    blog = db.query(query, {
        'id': id,
    }, one=True)
    print blog
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
        }
    )
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


def tags_by_blog_id(id):
    tags = db.query(
        'match (:Blog{id: {id}})-[rel:has_tag]->(tag) '
        'return tag.content order by rel.index asc', {
            'id': id,
        }, cols=1)
    return tags


def update_tags(blog):
    tags = blog.get('tags', [])
    for i, tag in enumerate(tags):
        print 'update tag', tag
        db.query('match (blog:Blog{id: {id}}) '
                 'merge (blog)-[:has_tag{index: {index}}]->'
                 '(tag:Tag{content: {tag}})', {
                     'id': blog['id'],
                     'index': i,
                     'tag': tag,
                 })
    r = db.query('match (blog:Blog{id: {id}})-[rel:has_tag]->(tag) '
             'where not tag.content in {tags} '
             'delete rel', {
                 'id': blog['id'],
                 'tags': tags,
             })
    print 'delete tags'
    print r


def get_blog_preds():
    user = user_util.current_user()
    username = user and user.get('username', None)

    preds = ''
    if username != 'fans656':
        preds += ('''
            and not ((blog)-[:has_tag]->(:Tag{content: '_secret'}))
            and not ((blog)-[:has_tag]->(:Tag{content: '_me'}))
                  ''')
    return preds
