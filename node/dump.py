# coding: utf-8
import json
from pprint import pprint

from node import Node, Link

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
    return {
        'nodes': nodes,
        'links': links,
    }

def json_dump(node, fname=None, purge=False, **kwargs):
    nodes, links = node.reachable_nodes_and_links
    try:
        old = json_load(fname)
    except Exception:
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
    from blog import Blog
    blog = Blog(u'这是内容', title=u'今天好吗', tags=['test', u'测试'])
    json_dump(blog, 't.json', indent=2)
    #blog = Blog(u'change', title=u'noname', tags=[])
    #json_dump(blog, 't.json', indent=2)
    #print json_dump(blog, indent=2)
    #r = json_load('t.json')
    #pprint(r)
