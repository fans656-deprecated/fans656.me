# coding: utf-8
from mockclient import get, post

r = get('/api/node/1')
assert r['errno'] == 0

r = get('/api/node/99999')
assert r['errno'] == 404

print 'finished successfully'
