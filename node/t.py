# coding: utf-8
from dump import json_dump, json_load
from blog import Blog

json_dump(Blog(
    title=u'貌似可以了',
    content='skdjfqowifjqwoeijfwoeqifj'
), 't.json')
g = json_load('t.json')
import sys; reload(sys); sys.setdefaultencoding('utf-8')
print g[lambda n: n.type == 'text.blog']
