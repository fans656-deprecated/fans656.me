# coding: utf-8
from blog import Blog
from dump import dump

blog = Blog(u'这是内容', title=u'今天好吗', tags=['test', u'测试'])
dump(blog)
