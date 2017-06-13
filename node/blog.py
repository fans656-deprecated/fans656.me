from node import Node

class Blog(Node):

    def __init__(self, content, title=None, tags=None):
        super(Blog, self).__init__(content, 'text.blog')
        if not isinstance(content, Node):
            title = title or ''
            tags = tags or []
            self.link(Node(title, 'text.title'), type='title')
            for tag in tags:
                self.link(Node(tag, 'text.tag'), type='tag')

    @property
    def title(self):
        return self['title']

    @property
    def content(self):
        return self.val

    @property
    def tags(self):
        return [unicode(tag) for tag in self['tag']]
