from flask import request

import user
import session

def get_cookie():
    data = request.get_json(force=True, silent=True)
    if not data or len(data) > 512:
        return ''
    username = data.get('username', '')
    password = data.get('password', '')
    if not user.valid_auth(username, password):
        return ''
    return session.new_session(username)
