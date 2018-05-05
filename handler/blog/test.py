# coding: utf-8
import requests


print requests.put('http://localhost:3000/blog', json={
    'content': u'''
type: pic

# 这是标题

this is just a test
    '''.strip()
}).content
