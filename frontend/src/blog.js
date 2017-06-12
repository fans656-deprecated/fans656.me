import React, { Component } from 'react';
import { Link } from 'react-router-dom';

class BlogContent extends Component {
  render() {
    const blog = this.props.blog;
    return (
      <article key={blog.id}>
        <div className="title">
          {blog.title ? <h1>{blog.title}</h1> : null}
        </div>
        <div className="paragraphs">
          {blog.content.split('\n').map(paragraph => <p>{paragraph}</p>)}
        </div>
        <div className="datetime">
          <Link to={url}>{blog.ctime.toLocaleDateString()}</Link>
        </div>
      </article>
    );
  }
}

export class Blog extends Component {
  render() {
    const blog = this.props.blog;
    return (
      <div>
        <BlogContent content={blog.content} />
      </div>
    );
  }
}

export class Blogs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blogs: [],
    };
  }
  
  componentDidMount() {
    this.getBlogs();
  }
  
  getBlogs = async () => {
    const title = this.props.title;
    let url = '/api/blog';
    if (title) {
      url += '/' + encodeURIComponent(title);
    }
    const res = await fetchJSON('GET', url, {
      username: this.props.username,
      id: this.props.id,
    });
    const blogs = res.blogs.map((blog) => {
      blog.ctime = new Date(blog.ctime);
      blog.mtime = new Date(blog.mtime);
      return blog;
    });
    if (res.ok) {
      this.setState({blogs: blogs});
    }
  }
  
  render() {
    const blogs = this.state.blogs.map((blog) => {
      const url = '/blog/?id=' + blog.id;
      return (
        <article key={blog.id}>
          <div className="title">
            {blog.title ? <h1>{blog.title}</h1> : null}
          </div>
          <div className="paragraphs">
            {paragraphs.map(paragraph => <p>{paragraph}</p>)}
          </div>
          <div className="datetime">
            <Link to={url}>{blog.ctime.toLocaleDateString()}</Link>
          </div>
        </article>
      );
    });
    let sticky;
    if (this.props.user) {
      sticky = (
        <div className="sticky">
          <div className="tooltip-container">
            <Link to="/new-blog"><Icon type={IconPlus}/></Link>
            <div className="tooltip reverse-color">New blog</div>
          </div>
        </div>
      );
    }
    return (
      <div className="center narrow">
        <div className="blogs">
          {blogs}
        </div>
        {sticky}
      </div>
    );
  }
}

export class EditBlog extends Component {
  constructor(props) {
    super(props);
    const state = Plain.deserialize('Enter your blog here...');
    this.state = {
      state: state,
    }
  }
  
  onChange = (state) => {
    this.setState({state})
  }
  
  doPost = async () => {
    const state = this.state.state;
    const content = Plain.serialize(state);
    const res = await fetchJSON('POST', '/api/blog', {
      title: this.title.value,
      content: content,
    });
    if (res.ok) {
      console.log(res);
      this.props.history.push('/');
    } else {
      console.log(res);
    }
  }

  render() {
    return (
      <div className="center wide">
        <input ref={(input) => this.title = input}
          placeholder="Enter your title here..."
          style={{
            minWidth: '800px',
            marginBottom: '1em',
            lineHeight: '1.2',
            padding: '.6em',
          }}
        />
        <Editor className="editor"
          style={{
            minWidth: '800px',
            minHeight: '100px',
            padding: '.5em',
          }}
          state={this.state.state}
          onChange={this.onChange}
        />
        <button onClick={this.doPost}
          style={{float: 'right', marginTop: '1em'}}
        >Post</button>
      </div>
    );
  }
}
