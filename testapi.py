# coding: utf-8
import subprocess
import json

def post(url, data=None):
    data = data or {}
    url = 'http://localhost:6561' + url
    cmd = '''curl -s -X POST -H 'Content-Type: application/json' -d '{data}' {url}'''.format(
        url=url, data=json.dumps(data))
    r = subprocess.check_output(cmd, shell=True)
    return r

print post('/api/node', {
    'type': 'blog',
    'content': u'马上睡觉',
    'title': u'是的',
    'tags': [u'困了', u'sleep'],
})
