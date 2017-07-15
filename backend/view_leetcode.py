import json
import itertools
from datetime import timedelta

from dateutil.parser import parse as parse_datetime

import db
from util import success_response, error_response

def get_statistics():
    blogs = db.query('''
        match (blog:Blog)-[:has_tag]->(:Tag{content: "leetcode"})
        return blog
                     ''', cols=1)
    blogs_by_day = [
        {'blogs': list(blogs), 'date': date} for date, blogs in
        itertools.groupby(blogs,
                          lambda blog: (parse_datetime(blog['ctime']) + timedelta(hours=8)).date())
    ]
    blogs_by_day.sort(key=lambda o: o['date'])
    blog_links = [[{
        'url': '/blog/{}'.format(blog['id']),
        'date': blog['ctime'],
        'title': json.loads(blog['leetcode'])['title']
    } for blog in item['blogs']] for item in blogs_by_day]

    date = blogs_by_day[0]['date']
    date_end = blogs_by_day[-1]['date']

    all_blogs_by_day = []
    i = 0
    while date <= date_end:
        if blogs_by_day[i]['date'] == date:
            item = blogs_by_day[i]
            i += 1
        else:
            item = {'blogs': [], 'date': date}
        all_blogs_by_day.append(item)
        date += timedelta(days=1)

    dates = [item['date'] for item in all_blogs_by_day]
    counts = [len(item['blogs']) for item in all_blogs_by_day]
    data = {
        'dates': dates,
        'counts': counts,
        'blog_links': blog_links,
        'total': sum(counts),
    }
    return success_response(data)
