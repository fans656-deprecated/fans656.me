from utils import require_login

@require_login
def post_blog(session):
    return 'hi, {}, wanna post something?'.format(session.username)
