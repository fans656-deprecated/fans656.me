import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import IconCaretLeft from 'react-icons/lib/fa/caret-left'
import IconCaretRight from 'react-icons/lib/fa/caret-right'
import IconPlus from 'react-icons/lib/md/add'
import IconSearch from 'react-icons/lib/md/search'
import qs from 'qs'
import $ from 'jquery'

import Blog from './Blog'
import { Icon, DangerButton, Textarea, Input } from './common'
import { fetchJSON, fetchData } from './utils'

export default class Blogs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blogs: [],
      pagination: {},
    };
  }

  componentDidMount() {
    this.fetchBlogs();
    $('.blog-content img').each((img) => {
      console.log(img.attr('src'));
      img.click(() => {
        window.open(img.attr('src'), '_blank');
      });
    });
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
    }, data => {
      let blogs = data.blogs;
      this.setState({
        blogs: blogs,
        pagination: {
          page: data.page,
          size: data.size,
          total: data.total,
          nPages: data.n_pages,
        },
      });
    });
  }

  navigateToNthPage = (page) => {
    console.log('navigate to page', page);
    this.setState({
      navigation: {page: page}
    });
  }

  render() {
    const owner = this.props.owner;
    const user = this.props.user;
    const isOwner = user && owner === user.username;
    const blogs = this.state.blogs.map((blog, i) => (
      <Blog
        key={blog.id}
        blog={blog}
        isOwner={isOwner}
        user={user}
      />
    ));
    //const pagination = this.state.pagination;
    return <div>
      <div className="blogs">
        {blogs}
      </div>
      <Pagination {...this.state.pagination}
        onNavigate={this.navigateToNthPage}
      />
      <Panel isOwner={isOwner}/>
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
    if (this.props.id) {
      this.fetchBlog(this.props.id);
    }
  }

  fetchBlog = async (id) => {
    fetchData('GET', `/api/blog/${id}`, res => {
      this.setState({blog: res.blog});
    });
  }

  render() {
    const owner = this.props.owner;
    const user = this.props.user;
    const isOwner = user && owner === user.username;
    const blog = this.state.blog;
    if (!blog) {
      return null;
    }
    return (
      <div className="single-blog-view">
        <Blog
          key={blog.id}
          blog={blog}
          isOwner={isOwner}
          user={user}
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
    const res = await fetchJSON('GET', `/api/blog/${id}`);
    if (res.errno) {
      console.log('error', res);
      alert(res.detail);
    } else {
      const blog = res.blog;
      const tags = blog.tags || [];
      this.setState({
        blog: blog,
        text: blog.content,
        tagsText: tags.join(', '),
      });
    }
  }

  onEditorTextChange = ({target}) => {
    this.setState({text: target.value});
  }

  doPost = async () => {
    const blog = this.state.blog;

    blog.content = this.state.text;
    blog.customUrl = this.customUrlInput.val() || undefined

    const tags = this.state.tagsText.split(/[,，]/)
      .map(tag => tag.trim())
      .filter(nonempty => nonempty);
    blog.tags = tags;

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
    if (!this.props.user) {
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
    console.log('isDesktop', isDesktop);
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

  render() {
    const items = [
      <li onClick={this.toggleConsole} key="console"><a>
        <Icon title="Search" type={IconSearch}/>
      </a></li>
    ];
    if (this.props.isOwner) {
      items.push(
        <li key="new-blog">
          <Link to="/new-blog" title="New blog"><Icon type={IconPlus} /></Link>
        </li>
      );
    }
    return <ul id="panel" className="panel">
      {items}
    </ul>;
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
    console.log('navigateToNthPage', page);
    try {
      page = parseInt(page, 10);
      const options = qs.parse(window.location.search.slice(1));
      const size = options.size;
      let url = '/blog';
      if (page === 1) {
        if (size) {
          url += `?size=${size}`;
        }
      } else if (1 < page && page <= this.props.nPages) {
        url += `?page=${page}`;
        if (size) {
          url += `&size=${size}`;
        }
      } else {
        console.log('wrong page', page);
        return;
      }
      console.log('do navigateToNthPage', url);
      window.location.href = url;
    } catch (e) {
      console.log(e);
    }
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
      <a href={`/blog?page=${Math.max(this.state.page - 1, 1)}`}>
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
      <a href={`/blog?page=${Math.min(this.state.page + 1, this.props.nPages)}`}>
        <Icon type={IconCaretRight} size="large"/>
      </a>
    </div>
  }
}
Pagination = withRouter(Pagination);
