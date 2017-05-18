from flask import Flask, request, jsonify

USERS = {
    'fans656': 'test',
}

app = Flask(__name__)

def error(detail):
    return jsonify({'status': 'error', 'detail': detail})

@app.route('/login')
def login():
    username = request.args.get('username', None)
    if username is None:
        return error('username required')
    try:
        passwd = USERS[username]
    except KeyError:
        return error('user does not exist')

