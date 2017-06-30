import view_user, view_node, view_blog

endpoints = [
    ('POST', '/api/login', view_user.post_login),
    ('POST', '/api/register', view_user.post_register),
    ('GET', '/api/logout', view_user.get_logout),
    ('GET', '/api/me', view_user.get_me),
    ('GET', '/api/profile/<username>', view_user.get_profile),
    ('POST', '/profile/<username>/avatar', view_user.post_avatar),

    ('POST', '/api/node', view_node.post_node),
    ('PUT', '/api/node/<persisted_id>', view_node.put_node),
    ('GET', '/api/node', view_node.get_nodes),

    ('POST', '/api/blog', view_blog.post_blog),
    ('GET', '/api/blog', view_blog.get_blogs),
    ('GET', '/api/blog/<persisted_id>', view_blog.get_blog),
    ('PUT', '/api/blog/<persisted_id>', view_blog.put_blog),
    ('DELETE', '/api/blog/<persisted_id>', view_blog.del_blog),

    ('POST', '/api/blog/<blog_id>/comment', view_blog.post_comment),
    ('GET', '/api/blog/<blog_id>/comment', view_blog.get_comments),
]
