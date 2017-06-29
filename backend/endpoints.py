import view_user, view_node, view_blog

endpoints = [
    ('POST', '/api/login', view_user.post_login),
    ('GET', '/api/logout', view_user.get_logout),
    ('GET', '/api/me', view_user.get_me),

    ('POST', '/api/node', view_node.post_node),
    ('PUT', '/api/node/<int:node_id>', view_node.put_node),
    ('GET', '/api/node', view_node.get_nodes),

    ('POST', '/api/blog', view_blog.post_blog),
    ('GET', '/api/blog', view_blog.get_blogs),
    ('GET', '/api/blog/<int:node_id>', view_blog.get_blog),
    ('PUT', '/api/blog/<int:node_id>', view_blog.put_blog),
    ('DELETE', '/api/blog/<int:node_id>', view_blog.del_blog),
]
