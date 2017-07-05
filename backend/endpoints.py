import view_user, view_node, view_blog, view_console, view_misc, view_file
import view_read

endpoints = [
    # login
    ('POST', '/api/login', view_user.post_login),
    ('POST', '/api/register', view_user.post_register),
    ('GET', '/api/logout', view_user.get_logout),
    ('GET', '/api/me', view_user.get_me),

    # profile
    ('GET', '/api/profile/<username>', view_user.get_profile),
    ('GET', '/profile/<username>/avatar', view_user.get_avatar),
    ('POST', '/profile/<username>/avatar', view_user.post_avatar),

    # blog
    ('POST', '/api/blog', view_blog.post_blog),
    ('GET', '/api/blog', view_blog.get_blogs),
    ('GET', '/api/blog/<id>', view_blog.get_blog),
    ('PUT', '/api/blog/<id>', view_blog.put_blog),
    ('DELETE', '/api/blog/<id>', view_blog.del_blog),

    ('POST', '/api/blog/search', view_blog.search),

    # comment
    ('POST', '/api/blog/<blog_id>/comment', view_blog.post_comment),
    ('GET', '/api/blog/<blog_id>/comment', view_blog.get_comments),
    ('DELETE', '/api/comment/<comment_id>', view_blog.delete_comments),

    # file
    ('POST', '/api/file/<path:fpath>', view_file.post_file),
    ('GET', '/api/file', view_file.list_root_file_directory),
    ('GET', '/api/file/<path:dirpath>', view_file.list_file_directory),

    # read
    ('GET', '/api/read/<blog_id>', view_read.get_read),

    # misc
    ('GET', '/api/custom-url/<path:path>', view_misc.get_custom_url),
    ('GET', '/api/<path:path>', view_misc.no_such_api),

    ('GET', '/static/<path:path>', view_misc.get_static),
    ('GET', '/file/<path:path>', view_misc.get_file),
]
