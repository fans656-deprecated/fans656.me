import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import IconCaretLeft from 'react-icons/lib/fa/caret-left'
import IconCaretRight from 'react-icons/lib/fa/caret-right'
import IconPlus from 'react-icons/lib/md/add'
//import IconSearch from 'react-icons/lib/md/search'
import qs from 'qs'
import $ from 'jquery'

import Blog from './Blog'
import { Icon, DangerButton, Textarea, Input } from './common'
import { fetchData } from './utils'

export default class Blogs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blogs: [],
      pagination: {},
      searched: null,
    };
  }

  componentDidMount() {
    this.props.registerConsoleHandler(this.consoleHandler);
    this.fetchBlogs();
    $('.blog-content img').each((img) => {
      img.click(() => {
        window.open(img.attr('src'), '_blank');
      });
    });
    $('#editor').focus();
  }

  componentWillUnmount() {
    this.props.unregisterConsoleHandler(this.consoleHandler);
  }

  consoleHandler = ({data}) => {
    if (!data || data.length === 0) {
      this.setState({searched: null});
    } else {
      const tags = data.split(',').map(s => s.trim()).filter(s => s.length > 0);
      fetchData('POST', '/api/blog/search', {
        by: 'tags',
        match: 'partial',
        tags: tags,
      }, res => {
        this.setState({
          searched: {
            blogs: res.blogs,
            pagination: res.pagination,
            tags: res.tags,
          }
        });
      });
    }
  }

  fetchBlogs = () => {
    const options = qs.parse(window.location.search.slice(1));
    const tags = options.tags || [];
    const page = options.page || 1;
    const size = options.size || 20;

    fetchData('GET', '/api/blog', {
      tags: tags,
      page: page,
      size: size,
    }, res => {
      this.setState({
        blogs: res.blogs,
        pagination: res.pagination,
      });
    });
  }

  navigateToNthPage = (page) => {
    this.setState({
      navigation: {page: page}
    });
  }

  render() {
    const user = this.props.user;
    let blogs, pagination, tags;
    let tagged = false;
    if (this.state.searched) {
      const searched = this.state.searched;
      blogs = searched.blogs;
      pagination = searched.pagination;
      tags = searched.tags;
    } else {
      blogs = this.state.blogs;
      pagination = this.state.pagination;
      tags = qs.parse(window.location.search.slice(1)).tags || [];
      if (tags.length !== 0) {
        tagged = true;
      }
    }
    blogs = blogs.map((blog, i) => (
      <Blog
        key={blog.id}
        blog={blog}
        user={this.props.user}
      />
    ));
    const total = pagination.total;
    const blogsPlural = total === 1 ? 'blog' : 'blogs';
    const tagsText = `${total} ${blogsPlural} tagged ${tags.join(', ')}`;
    return <div>
      {(this.state.searched || tagged) &&
          <p
            style={{
              width: '100%',
              marginTop: '1.2rem',
              marginBottom: '-2.0rem',
              textAlign: 'center',
              color: 'steelblue',
              fontSize: '.8rem',
            }}
          >{tagsText}</p>
      }
      <div className="blogs">
        {blogs}
      </div>
      <Pagination {...pagination}
        onNavigate={this.navigateToNthPage}
        tags={tags}
      />
      <Panel user={this.props.user}/>
    </div>
  }
}

export class ViewBlog extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blog: null,
    };
  }

  componentDidMount() {
    if (this.props.blog) {
      this.setState({blog: this.props.blog});
    } else if (this.props.id) {
      this.fetchBlog(this.props.id);
    }
  }

  fetchBlog = async (id) => {
    fetchData('GET', `/api/blog/${id}`, res => {
      this.setState({blog: res.blog});
    });
  }

  render() {
    const user = this.props.user;
    const blog = this.state.blog;
    if (!blog) {
      return null;
    }
    return (
      <div className="single-blog-view">
        <Blog
          key={blog.id}
          blog={blog}
          user={this.props.user}
          commentsVisible={true}
          isSingleView={true}
        />
      </div>
    )
  }
}

class EditBlog extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blog: {},
      title: '',
      text: '',
      tagsText: '',
    };
  }

  componentDidMount() {
    if (this.props.id) {
      this.fetchBlog(this.props.id);
    }
  }

  fetchBlog = async (id) => {
    fetchData('GET', `/api/blog/${id}`, res => {
      const blog = res.blog;
      const tags = blog.tags || [];
      this.setState({
        blog: blog,
        text: blog.content,
        tagsText: tags.join(', '),
      });
    });
  }

  onEditorTextChange = ({target}) => {
    this.setState({text: target.value});
  }

  doPost = async () => {
    const blog = this.state.blog;

    blog.content = this.state.text;
    blog.custom_url = this.customUrlInput.val() || undefined

    const tags = this.state.tagsText.split(/[,，]/)
      .map(tag => tag.trim())
      .filter(nonempty => nonempty);
    if (tags.length) {
      blog.tags = tags;
    }

    if (blog.id) {
      fetchData('PUT', `/api/blog/${blog.id}`, blog, this.after);
    } else {
      fetchData('POST', '/api/blog', blog, this.after);
    }
  }

  doDelete = async () => {
    fetchData('DELETE', `/api/blog/${this.state.blog.id}`, this.after);
  }

  after = () => {
    const blog = this.state.blog;
    const options = qs.parse(window.location.search.slice(1));

    let backURL;
    if (options['back-to-single-view']) {
      backURL = `/blog/${blog.id}`
    } else {
      backURL = '/blog';
    }

    this.props.history.push(backURL);
  }

  render() {
    if (!this.props.user.isLoggedIn()) {
      console.log('you are not logged in');
      return null;
    }
    return <div className="edit-blog">
      <Textarea
        className="content-edit"
        id="editor"
        value={this.state.text}
        onChange={this.onEditorTextChange}
        submit={this.doPost}
        ref={(editor) => this.editor = editor}
      ></Textarea>
      <Input className="tags"
        placeholder="Tags"
        type="text"
        value={this.state.tagsText}
        onChange={({target}) => this.setState({tagsText: target.value})}
        submit={this.doPost}
      />
      <Input className="custom-url"
        placeholder="Custom URL"
        type="text"
        submit={this.doPost}
        defaultValue={this.state.blog.custom_url}
        ref={ref => this.customUrlInput = ref}
      />
      <div className="buttons">
        <DangerButton id="delete" onClick={this.doDelete}>
          Delete
        </DangerButton>
        <button id="submit" className="primary" onClick={this.doPost}>
          Post
        </button>
      </div>
    </div>
  }
}
EditBlog = withRouter(EditBlog);
export { EditBlog };

class Panel extends Component {
  constructor(props) {
    super(props);
    this.scrolling = false;
    this.lastY = null;
  }

  componentDidMount() {
    // mobile panel auto hide
    const isDesktop = window.matchMedia('(min-device-width: 800px)').matches;
    if (isDesktop) {
      return;
    }
    $(window).scroll(ev => {
      this.scrolling = true;
    });
    const deltaY = 100;
    const duration = 300;
    const panel = $('#panel');
    panel.hide(duration);
    this.scrollTimer = setInterval(() => {
      if (this.scrolling) {
        const y = $(window).scrollTop();
        if (this.lastY === null) {
          this.lastY = y;
        } else {
          // scroll down enough
          if (y - this.lastY > deltaY) {
            panel.hide(duration);
            this.lastY = y;
            // scroll up enough
          } else if (this.lastY - y > deltaY) {
            panel.show(duration);
            this.lastY = y;
          }
        }
        this.scrolling = false;
      }
    }, 250);
  }

  componentWillUnmount() {
    clearInterval(this.scrollTimer);
  }

  showConsole = () => {
    this.setState({consoleVisible: true});
  }

  render() {
    const items = [
      //<li onClick={this.showConsole} key="console"><a>
      //  <Icon title="Search" type={IconSearch}/>
      //</a></li>
    ];
    if (this.props.user.isOwner()) {
      items.push(
        <li key="new-blog">
          <Link to="/new-blog" title="New blog"><Icon type={IconPlus} /></Link>
        </li>
      );
    }
    return (
      <ul id="panel" className="panel">
        {items}
      </ul>
    );
  }
}

class Pagination extends Component {
  constructor(props) {
    super(props);
    this.state = {
      page: null,
    };
  }

  componentWillReceiveProps(props) {
    this.setState({page: props.page});
  }

  onCurrentPageInputChange = ({target}) => {
    let page = target.value;
    if (page) {
      this.setState({page: page});
    }
  }

  navigateToNthPage = (page) => {
    window.location.href = this.getNavigationURL(page);
  }

  getNavigationURL = (page) => {
    page = parseInt(page, 10);

    const query = qs.parse(window.location.search.slice(1));

    page = Math.min(page, this.props.nPages);
    page = Math.max(page, 1);

    query.page = page;
    query.tags = [...new Set(
      (this.props.tags || []).concat(query.tags || [])
    )];
    if (!query.tags) {
      delete query.tags;
    }
    if (query.page === 1) {
      delete query.page;
    }

    const queryString = qs.stringify(query)
    const url = '/blog' + (queryString ? '?' + queryString : '');
    return url;
  }

  onKeyUp = (ev) => {
    if (ev.key === 'Enter') {
      this.navigateToNthPage(this.state.page);
    }
  }
  
  render() {
    if (!this.props.nPages) {
      return null;
    }
    return <div id="pagination">
      <a href={this.getNavigationURL(this.state.page - 1)}>
        <Icon type={IconCaretLeft} size="large"/>
      </a>
      <input
        id="current-page"
        type="text"
        value={this.state.page}
        onChange={this.onCurrentPageInputChange}
        onKeyUp={this.onKeyUp}
      />
      <span>&nbsp;/&nbsp;</span>
      <span className="n-pages">{this.props.nPages}</span>
      <a href={this.getNavigationURL(this.state.page + 1)}>
        <Icon type={IconCaretRight} size="large"/>
      </a>
    </div>
  }
}
Pagination = withRouter(Pagination);
