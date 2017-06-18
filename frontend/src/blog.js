import React, { Component } from 'react'
import { withRouter } from 'react-router-dom'
import IconTop from 'react-icons/lib/fa/chevron-up'
import IconPlus from 'react-icons/lib/fa/plus'

import { Link } from 'react-router-dom'
import { fetchJSON } from './utils'
import {
  NORMAL_ICON_SIZE, LARGE_ICON_SIZE, SMALL_ICON_SIZE
} from './constants'

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
      const paragraphs = node.data.split('\n').map((line, i) => (
        <p key={i}>{line || <br/>}</p>
      ));
      const ctime = new Date(node.ctime).toLocaleString()
      const url = `/blog/${node.id}` + (isOwner ? '/edit' : '');
      return <div className="blog" key={node.id}>
        <div className="paragraphs">
          {paragraphs}
        </div>
        <div className="ctime datetime">
          <Link to={url}>{ctime}</Link>
        </div>
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
    };
  }

  componentDidMount() {
    if (this.props.id) {
      this.fetchBlog(this.props.id);
    }
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
    let res;
    if (node.id) {
      res = await fetchJSON('PUT', `/api/node/${node.id}`, node);
    } else {
      node.links = [
        {'rel': 'type', 'dst': 'blog'},
        //{'rel': 'title', 'dst': 
      ];
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
      <input defaultValue={this.state.}/>
      <textarea
        id="editor"
        value={this.state.text}
        onChange={this.onEditorTextChange}
        ref={(editor) => this.editor = editor}
      ></textarea>
      <button className="submit" onClick={this.post}>Post</button>
    </div>
  }
}
EditBlog = withRouter(EditBlog);
export { EditBlog };

class Panel extends Component {
  render() {
    return <div className="panel">
      <Link to="/new-blog"><IconPlus size={NORMAL_ICON_SIZE}/></Link>
    </div>;
  }
}
