from node import Node, encoding

class Blog(Node):

    def __init__(self, content, title=None, tags=None):
        super(Blog, self).__init__(content, 'text.content')
        title = title or ''
        tags = tags or []
        self.link(Node(title, 'text.title'), type='title')
        for tag in tags:
            self.link(Node(tag, 'text.tag'), type='tag')

    @property
    def title(self):
        return self['title'].encode(encoding)

    @property
    def content(self):
        return self.val.encode(encoding)

    @property
    def tags(self):
        return [tag.encode(encoding) for tag in self['tag']]

    #def __iter__(self):
    #    return iter([
    #        ('content', self.content),
    #        ('title', self.title),
    #        ('tags', self.tags),
    #    ])
