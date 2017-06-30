import React, { Component } from 'react'

import { fetchJSON } from './utils'

export default class Comments extends Component {
  constructor(props) {
    super(props);
    this.state = {
      comments: [],
    };
  }

  componentDidMount = () => {
    if (this.props.visible) {
      this.fetchComments();
    }
  }

  fetchComments = async () => {
    const blog = this.props.blog;
    const res = await fetchJSON('GET', `/api/blog/${blog.persisted_id}/comment`);
    if (res.errno === 0) {
      this.setState({comments: res.comments});
    }
  }

  onCommentPost = () => {
    this.fetchComments();
  }

  render() {
    if (!this.props.visible) {
      return null;
    }
    const comments = this.state.comments.map(comment => (
      <Comment name={comment.visitor_name} content={comment.content}/>
    ));
    return <div className="comments-content"
    >
      {comments}
      <CommentEdit
        blog={this.props.blog}
        onPost={this.onCommentPost}
      />
    </div>
  }
}

const Comment = (props) => {
  return (
    <div className="comment">
      <div className="user" style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '.8em',
      }}>
        <img
          alt="fans656"
          src="http://ub:6560/file/Male-512.png"
          style={{
            width: 24, height: 24,
            borderRadius: '16px',
            border: '1px solid #ccc',
            marginRight: '.5em',
          }}
        />
        <span style={{
          position: 'relative',
          top: '.2em',
          marginBottom: '0',
        }}>
          {props.name}
        </span>
      </div>
      <div>{props.content}</div>
      <div style={{textAlign: 'right'}}>
        <span className="info">
          {new Date().toLocaleDateString()}
        </span>
      </div>
    </div>
  )
}


class CommentEdit extends Component {
  postComment = async () => {
    const blog = this.props.blog;
    const url = `/api/blog/${blog.persisted_id}/comment`;
    const res = await fetchJSON('POST', url, {
      'name': this.nameInput.value,
      'text': this.textarea.value,
    });
    if (res.errno) {
      console.log('error', res);
      alert(res.detail);
    } else {
      this.props.onPost();
      this.textarea.value = '';
    }
  }

  render() {
    return (
      <div>
        <textarea
          placeholder="Write your comment here"
          onKeyUp={({target}) => {
            target.style.height = '5px';
            target.style.height = target.scrollHeight + 15 + 'px';
          }}
          style={{
            boxSizing: 'border-box',
          }}
          ref={ref => this.textarea = ref}
        >
        </textarea>
        <div style={{
          display: 'flex',
          justifyContent: 'flex-end',
          width: '100%',
        }}>
          <input type="text" placeholder="Your name"
            ref={ref => this.nameInput = ref}
          />
          <button style={{marginRight: '0'}} onClick={this.postComment}>
            Post
          </button>
        </div>
      </div>
    )
  }
}
