import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import IconPlus from 'react-icons/lib/fa/plus'
import IconCaretLeft from 'react-icons/lib/fa/caret-left'
import IconCaretRight from 'react-icons/lib/fa/caret-right'
import qs from 'qs'
import $ from 'jquery'

import Blog from './Blog'
import { Icon, DangerButton, Textarea, Input } from './common'
import { fetchJSON, fetchData } from './utils'

export class Blogs extends Component {
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
      {isOwner && <Panel/>}
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
      return <h1>Not found</h1>
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
    return <div className="wide center edit-blog">
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
  render() {
    return <div className="panel">
      <Link to="/new-blog" title="New blog"><Icon type={IconPlus} /></Link>
    </div>;
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
