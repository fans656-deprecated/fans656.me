import json
from datetime import datetime
from pprint import pprint

import requests
from f6 import bunch

import db
from db import cypher

blogs_query = '''
select id, data, ctime from nodes
where id in (
    select l.src from links as l inner join nodes as n
    on l.dst = n.id
    where l.rel = 'type' and n.data = 'blog'
) order by ctime
'''

tags_query = '''
select l.src, n.data from links as l inner join nodes as n
on l.dst = n.id
where l.rel = 'tag'
'''

titles_query = '''
select l.src, n.data from links as l inner join nodes as n
on l.dst = n.id
where l.rel = 'title'
'''

sources_query = '''
select l.src, n.data from links as l inner join nodes as n
on l.dst = n.id
where l.rel = 'source'
'''


def make_blogs():
    blogs = {}
    for blog_id, data, ctime in db.query(blogs_query):
        blogs[blog_id] = bunch(
            data=data.decode('utf8'),
            ctime=str(ctime) + ' UTC',
            tags=[],
            title='',
            source='',
        )

    # add title
    for blog_id, title in db.query(titles_query):
        blogs[blog_id].title = title.decode('utf8')

    # add source
    for blog_id, source in db.query(sources_query):
        blogs[blog_id].source = source.decode('utf8')

    # add tags
    for blog_id, tag in db.query(tags_query):
        blogs[blog_id].tags.append(tag.decode('utf8'))

    return sorted(blogs.values(), key=lambda b: b.ctime, reverse=True)


def get_tagged_blogs(blogs):
    return [b for b in blogs if b.tags]


def get_music_blogs(blogs):
    return [b for b in blogs if '<div class="music">' in b.data]


def get_video_blogs(blogs):
    return [b for b in blogs if '<div class="video">' in b.data]


def get_migrated_blogs(blogs):
    return [b for b in blogs if b.source]


def translate_http_to_https(blog):
    lines = blog.data.split('\n')
    lines[0] = lines[0].replace('http', 'https')
    blog.data = '\n'.join(lines)


def purge():
    cypher('match (n) detach delete n')


def build_properties_str(properties):
    return u'{{{}}}'.format(u', '.join(
        u'{}: "{}"'.format(k, v) for k, v in properties.items()
    ))


if __name__ == '__main__':
    blogs = make_blogs()

    map(translate_http_to_https, get_music_blogs(blogs))
    map(translate_http_to_https, get_video_blogs(blogs))

    #blogs = blogs[:10]

    purge()

    blog_ids = []
    n = len(blogs)
    for i, blog in enumerate(blogs):
        params = {
            'content': blog.data,
            'ctime': blog.ctime,
            'mtime': blog.ctime,
        }
        if blog.title:
            params['title'] = blog.title
        if blog.tags:
            params['tags'] = blog.tags
        properties_str = '{{{}}}'.format(', '.join(
            '{name}: {{{name}}}'.format(name=property_name)
            for property_name in params.keys()
        ))

        query = u'create (blog:Blog{}) return id(blog)'.format(properties_str)
        r = cypher(query, params)
        assert 'data' in r
        blog_ids.append(r['data'][0][0])
        print '{}/{} creating blogs'.format(i + 1, n)

    # linking blogs by now/prev relationship
    print
    for i, (now_id, prev_id) in enumerate(zip(blog_ids[:-1], blog_ids[1:])):
        print '{}/{} linking {} -> {}'.format(i + 1, n - 1, now_id, prev_id)
        r = cypher('''
            match (now), (prev) where id(now) = {} and id(prev) = {}
            create (now)-[:previous_blog]->(prev)
               '''.format(now_id, prev_id))
        assert 'data' in r
