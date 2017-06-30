import React, { Component } from 'react'
import { Link } from 'react-router-dom'

import { fetchJSON, fetchData } from './utils'

export default class Comments extends Component {
  constructor(props) {
    super(props);
    this.state = {
      comments: [],
    };
  }

  componentDidMount() {
    this.fetchComments();
  }

  componentWillReceiveProps(props) {
    if (props.visible) {
      this.fetchComments();
    }
  }

  fetchComments = async () => {
    const blog = this.props.blog;
    const url =  `/api/blog/${blog.persisted_id}/comment`;
    fetchData('GET', url, res => {
      this.setState({comments: res.comments});
    });
  }

  onCommentPost = () => {
    this.fetchComments();
  }

  render() {
    if (!this.props.visible) {
      return null;
    }
    const comments = this.state.comments.map((comment, i) => (
      <Comment
        key={i}
        name={comment.visitor_name}
        content={comment.content}
      />
    ));
    return <div className="comments-content"
    >
      {comments}
      <CommentEdit
        user={this.props.user}
        blog={this.props.blog}
        onPost={this.onCommentPost}
      />
    </div>
  }
}

const Comment = (props) => {
  return (
    <div className="comment"
      style={{
        fontSize: '.9em',
      }}
    >
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
    const user = this.props.user;
    const isLoggedIn = user && user.username;
    return (
      <div>
        <textarea
          className="comment-edit"
          placeholder="Write your comment here..."
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
          //justifyContent: 'flex-end',
          width: '100%',
        }}>
          {!isLoggedIn &&
            <div>
              <input className="visitor-name"
                style={{
                  padding: '0 1em',
                  fontSize: '.8em',
                }}
                type="text"
                placeholder="Name"
                ref={ref => this.nameInput = ref}
              />
              <div style={{
                display: 'inline',
                fontSize: '.8em',
                color: '#aaa',
              }}>
                <span>&nbsp;or&nbsp;</span>
                <Link to="/register" style={{
                  color: '#777',
                }}>
                  Register
                </Link>
                <span>&nbsp;/&nbsp;</span>
                <Link to="/login" style={{
                  color: '#777',
                }}>
                  Login
                </Link>
              </div>
            </div>
          }
          <button
            style={{
              marginLeft: 'auto',
              marginRight: '1px',
              boxShadow: '0 0 2px #aaa',
            }}
            onClick={this.postComment}>
            Post
          </button>
        </div>
      </div>
    )
  }
}
