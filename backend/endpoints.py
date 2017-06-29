import views

endpoints = [
    ('POST', '/api/login', views.user.post_login),
    ('GET', '/api/logout', views.user.get_logout),
    ('GET', '/api/me', views.user.get_me),

    ('POST', '/api/node', views.node.post_node),
    ('PUT', '/api/node/<int:node_id>', views.node.put_node),
    ('GET', '/api/node', views.node.get_nodes),

    ('POST', '/api/blog', views.blog.post_blog),
    ('GET', '/api/blog', views.blog.get_blogs),
    ('GET', '/api/blog/<int:node_id>', views.blog.get_blog),
    ('PUT', '/api/blog/<int:node_id>', views.blog.put_blog),
    ('DELETE', '/api/blog/<int:node_id>', views.blog.del_blog),
]
