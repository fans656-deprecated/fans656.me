import json


route = '/blog'


def handle(**env):
    request = env['request']
    if request.method != 'PUT':
        return 'error', 400
    data = request.get_json()
    return json.dumps(data)
