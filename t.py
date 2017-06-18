from pprint import pprint

import node

nodes = node.query({'ref': 'blog'})
nodes = map(dict, nodes)
for node in nodes:
    pprint(node)
