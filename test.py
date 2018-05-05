import json

import requests


r = requests.put('http://localhost:3000/api/route', json={
    'route': '/',
    'type': 'package',
    'data': json.dumps({
        'name': 'home',
    })
})
print r.content
