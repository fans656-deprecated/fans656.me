from flask import current_app as app
from flask import request

from utils import require_login

@require_login
def api_post_blog(session):
    username = session.username
    print 'username wanna post {}'.format(request.json)
    return 'hello {}'.format(username)
