import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import IconPlus from 'react-icons/lib/fa/plus'
import IconCaretLeft from 'react-icons/lib/fa/caret-left'
import IconCaretRight from 'react-icons/lib/fa/caret-right'
import qs from 'qs'
import $ from 'jquery'

import Comments from './Comments'
import { Icon, DangerButton, Textarea, Input } from './common'
import { fetchJSON, fetchData } from './utils'

export class Blog extends Component {
  constructor(props) {
    super(props);
    this.state = {
      commentsVisible: false,
      numNewComments: 0,
    };
  }

  onCommentPost = () => {
    this.setState(prevState => {
      return {numNewComments: prevState.numNewComments + 1};
    });
  }

  render() {
    const isOwner = this.props.isOwner;
    const blog = this.props.blog;
    let title = blog.title || '';
    const url = `/blog/${blog.id}` + (isOwner ? '/edit' : '');
    const ctime = new Date(blog.ctime).toLocaleDateString()
    const tags = (blog.tags || []).map((tag, i) => {
      return <a className="tag info"
        key={i}
        href={`/blog?tag=${tag}`}
      >
        {tag}
      </a>
    });
    return <div className="blog">
      <a
        className="anchor"
        href={url}
        style={{position: 'absolute', left: '25%'}}
      >
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      </a>
      {title && <h2>{title}</h2>}
      <ReactMarkdown className="blog-content" source={blog.content}/>
      <div className="footer">
        <div>
          <div className={'comments '
              + (this.state.commentsVisible ? '' : 'info')}>
            <div
              className="clickable"
              onClick={() => this.setState((prevState) => {
                return {
                  commentsVisible: !prevState.commentsVisible
                };
              })}
            >
              <a href="#number-of-comments" className="number"
                onClick={ev => ev.preventDefault()}
              >
                {(blog.n_comments || 0) + this.state.numNewComments}&nbsp;
              </a>
              <span>Comments</span>
            </div>
          </div>
        </div>
        <div className="right">
          <div className="tags">{tags}</div>
          <div className="ctime datetime">
            {isOwner
                ? (
                  <Link
                    className="info"
                    to={url}
                    title={new Date(blog.ctime).toLocaleString()}
                  >{ctime}</Link>
                ) : (
                  <span
                    className="info"
                    title={new Date(blog.ctime).toLocaleString()}
                  >{ctime}</span>
                )
            }
          </div>
        </div>
      </div>
      <Comments
        visible={this.state.commentsVisible}
        user={this.props.user}
        blog={this.props.blog}
        onPost={this.onCommentPost}
      />
    </div>
  }
}

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
    const page = options.page || 1;
    const size = options.size || 20;

    fetchData('GET', '/api/blog', {
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
  render() {
    return <div className="wide center edit-blog">
      <Textarea></Textarea>
      <button className="submit">Post</button>
    </div>
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

  post = async () => {
    const blog = this.state.blog;

    blog.content = this.state.text;

    const tags = this.state.tagsText.split(/[,，]|  /)
      .map(tag => tag.trim())
      .filter(nonempty => nonempty);
    blog.tags = tags;

    const after = () => this.props.history.push('/blog');
    if (blog.id) {
      fetchData('PUT', `/api/blog/${blog.id}`, blog, after);
    } else {
      fetchData('POST', '/api/blog', blog, after);
    }
  }

  delete = async () => {
    const blog = this.state.blog;
    const res = await fetchJSON('DELETE', `/api/blog/${blog.id}`);
    if (res.errno) {
      alert(res.detail);
    } else {
      this.props.history.push('/blog');
    }
  }

  render() {
    return <div className="wide center edit-blog">
      <Textarea
        id="editor"
        value={this.state.text}
        onChange={this.onEditorTextChange}
        submit={this.post}
        ref={(editor) => this.editor = editor}
      ></Textarea>
      <Input className="tags"
        type="text"
        value={this.state.tagsText}
        submit={this.post}
        onChange={({target}) => this.setState({tagsText: target.value})}
      />
      <div className="buttons">
        <DangerButton id="delete" onClick={this.delete}>
          Delete
        </DangerButton>
        <button id="submit" className="primary" onClick={this.post}>
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
