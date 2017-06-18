# coding: utf-8
import json
from pprint import pprint

from node import Node, Link, Graph

def json_load(fname):
    with open(fname) as f:
        d = json.load(f)
        dict_nodes = d['nodes']
        dict_links = d['links']
    nodes = [Node(d['val'], d['type']) for d in dict_nodes]
    hash_to_node = {n.hash: n for n in nodes}
    links = [Link(d['val'],
                  src=hash_to_node[d['src']],
                  dst=hash_to_node[d['dst']])
             for d in dict_links]
    for link in links:
        link.src.dst_links.append(link)
        link.dst.src_links.append(link)
    return Graph(nodes, links)

def json_dump(node, fname=None, purge=False, **kwargs):
    nodes, links = node.reachable_nodes_and_links
    try:
        old = dict(json_load(fname))
    except Exception as e:
        old = {'nodes': [], 'links': []}
    new = {
        'nodes': map(dict, list(set(nodes) | set(old['nodes']))),
        'links': map(dict, list(set(links) | set(old['links']))),
    }
    if fname:
        with open(fname, 'w') as f:
            json.dump(new, f, **kwargs)
    else:
        return json.dumps(new, **kwargs)

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    from blog import Blog
    blog = Blog(u'这是内容', title=u'今天好吗', tags=['test', u'测试'])
    json_dump(blog, 't.json', indent=2)
    blog = Blog(u'change', title=u'noname', tags=[])
    json_dump(blog, 't.json', indent=2)

    graph = json_load('t.json')
    blogs = map(Blog, graph[lambda node: node.type == 'text.blog'])
    for blog in blogs:
        print 'Title:', blog.title
        print 'Tags:', blog.tags
        print 'Content:', blog.content.encode('utf8')
        print
