import json
import itertools
from datetime import timedelta

from dateutil.parser import parse as parse_datetime

import db
from util import success_response, error_response

def ctime_to_date(ctime):
    return (parse_datetime(ctime) + timedelta(hours=8)).date()

def get_statistics():
    blogs = db.query('''
        match (blog:Blog)-[:has_tag]->(:Tag{content: "leetcode"})
        return blog
                     ''', cols=1)
    blogs.sort(key=lambda blog: parse_datetime(blog['ctime']))
    blogs_by_day = [
        {'blogs': list(g), 'date': date} for date, g in
        itertools.groupby(blogs, lambda blog: ctime_to_date(blog['ctime']))
    ]
    blog_links = [[{
        'url': '/blog/{}'.format(blog['id']),
        'date': blog['ctime'],
        'title': json.loads(blog['leetcode'])['title']
    } for blog in item['blogs']] for item in blogs_by_day]

    date_beg = blogs_by_day[0]['date']
    date_end = blogs_by_day[-1]['date']
    n_days = (date_end - date_beg).days + 1

    all_blogs_by_day = [{
        'date': date_beg + timedelta(days=i),
        'blogs': [],
    } for i in xrange(n_days)]
    for item in blogs_by_day:
        idx = (item['date'] - date_beg).days
        all_blogs_by_day[idx]['date'] = item['date']
        all_blogs_by_day[idx]['blogs'] = item['blogs']

    dates = [item['date'] for item in all_blogs_by_day]
    counts = [len(item['blogs']) for item in all_blogs_by_day]
    data = {
        'dates': dates,
        'counts': counts,
        'blog_links': blog_links,
        'total': sum(counts),
    }
    return success_response(data)
