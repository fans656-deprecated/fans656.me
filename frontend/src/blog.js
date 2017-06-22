import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import IconPlus from 'react-icons/lib/fa/plus'
import $ from 'jquery'

import { Icon } from './common'
import { fetchJSON } from './utils'

export class Blog extends Component {
  render() {
    return <h1>todo</h1>;
  }
}

export class Blogs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blogNodes: [],
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

  fetchBlogs = async () => {
    const resp = await fetchJSON('GET', '/api/node?type=blog');
    this.setState({blogNodes: resp.nodes});
  }

  render() {
    const owner = this.props.owner;
    const user = this.props.user;
    const isOwner = user && owner === user.username;
    const blogs = this.state.blogNodes.map((node, i) => {
      const ctime = new Date(node.ctime).toLocaleString()
      const url = `/blog/${node.id}` + (isOwner ? '/edit' : '');
      return <div className="blog" key={node.id}>
        <a
          className="anchor"
          href={url}
          style={{position: 'absolute', left: '25%'}}
        >
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        </a>
        <ReactMarkdown className="blog-content" source={node.data}/>
        <div className="ctime datetime">
          <Link to={url}>{ctime}</Link>
        </div>
        <div className="hr"/>
      </div>
    });
    return <div>
      <div className="blogs">
        {blogs}
      </div>
      {isOwner && <Panel/>}
    </div>
  }
}

export class ViewBlog extends Component {
  render() {
    return <div className="wide center edit-blog">
      <textarea></textarea>
      <button className="submit">Post</button>
    </div>
  }
}

class EditBlog extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blogNode: {},
      title: '',
      text: '',
      tagsText: '',
    };
  }

  componentDidMount() {
    if (this.props.id) {
      this.fetchBlog(this.props.id);
    }
    $('#editor').keydown((e) => {
      console.log(e);
      // ctrl-enter
      if (e.ctrlKey && e.keyCode === 13) {
        $('#submit').click();
      } else if (e.keyCode === 9 && !e.ctrlKey) {
        e.preventDefault();
        $('#editor')[0].value += '    ';
      }
    });
  }

  fetchBlog = async (id) => {
    const res = await fetchJSON('GET', `/api/node/${id}`);
    if (res.errno) {
      console.log(res);
    } else {
      this.setState({blogNode: res.node, text: res.node.data});
      console.log('fetchBlog');
      console.log(res);
    }
  }

  onEditorTextChange = ({target}) => {
    this.setState({text: target.value});
  }

  post = async () => {
    const node = this.state.blogNode;
    node.data = this.state.text;
    node.links = [{rel: 'type', dst: 'blog'}];
    const tags = this.state.tagsText.split(',').map((tag) => tag.trim());
    for (const tag of tags) {
      node.links.push({rel: 'tag', dst: {data: tag}});
    }
    console.log(node);
    let res;
    if (node.id) {
      res = await fetchJSON('PUT', `/api/node/${node.id}`, node);
    } else {
      res = await fetchJSON('POST', '/api/node', node);
    }
    console.log('res');
    console.log(res);
    if (res.errno) {
      alert(res.detail);
    } else {
      this.props.history.push('/blog');
    }
  }

  render() {
    return <div className="wide center edit-blog">
      {/*<input defaultValue={this.state.}/>*/}
      <textarea
        id="editor"
        value={this.state.text}
        onChange={this.onEditorTextChange}
        ref={(editor) => this.editor = editor}
      ></textarea>
      <input type="text"
        style={{width: '100%'}}
        value={this.state.tagsText}
        onChange={({target}) => this.setState({tagsText: target.value})}
      />
      <button id="submit" className="submit" onClick={this.post}>Post</button>
    </div>
  }
}
EditBlog = withRouter(EditBlog);
export { EditBlog };

class Panel extends Component {
  render() {
    return <div className="panel">
      <Link to="/new-blog"><Icon type={IconPlus} /></Link>
    </div>;
  }
}
