import React, { Component } from 'react'
import { Link } from 'react-router-dom'

import { fetchData } from './utils'

export default class Comments extends Component {
  constructor(props) {
    super(props);
    this.state = {
      comments: [],
    };
  }

  componentDidMount() {
    if (this.props.visible) {
      this.fetchComments();
    }
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
    const comments = this.state.comments.map((comment, i) => {
      console.log('Comment', comment);
      return <Comment
        key={i}
        comment={comment}
        username={comment.username}
        user={comment.user}
        isVisitor={comment.is_visitor}
        ctime={comment.ctime}
        content={comment.content}
      />
    });
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

class Comment extends Component {
  constructor(props) {
    super(props);
    this.state = {
      avatarURL: '/file/anonymous.png',
    };
    const comment = props.comment;
    if (!comment.is_visitor) {
      fetchData('GET', `/profile/${comment.username}/avatar`, res => {
        this.setState({avatarURL: res.avatar_url});
      });
    }
  }

  render() {
    const comment = this.props.comment;
    const ctime = new Date(this.props.ctime);
    return (
      <div className="comment"
        style={{
          fontSize: '.9em',
          paddingBottom: '1em',
        }}
      >
        <div style={{
          display: 'flex',
        }}>
          <div className="user" style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '.2em',
          }}>
            <img
              alt={comment.username}
              src={this.state.avatarURL}
              style={{
                width: 24, height: 24,
                borderRadius: '16px',
                marginRight: '.5em',
              }}
            />
            <span style={{
              position: 'relative',
              top: '.2em',
            }}>
              {comment.username}
            </span>
          </div>
          <span className="datetime info" style={{marginLeft: 'auto',}}>
            {ctime.toLocaleString()}
          </span>
        </div>
        <div>
          {comment.content.split('\n').map(line =>
            <p style={{margin: '0'}}>{line}</p>)
          }
        </div>
      </div>
    )
  }
}


class CommentEdit extends Component {
  doPost = async () => {
    const content = this.textarea.value;
    if (content.length === 0) {
      alert('Empty?');
      return;
    }
    let comment = {
      content: content,
    };
    const user = this.props.user;
    if (user) {
      comment.user = user;
    } else {
      comment.visitorName = this.nameInput.value;
    }
    console.log(comment);

    const blog = this.props.blog;
    const url = `/api/blog/${blog.persisted_id}/comment`;
    fetchData('POST', url, comment, () => {
      this.props.onPost();
      this.textarea.value = null;
    });
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
                placeholder="Who are you? (name or email)"
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
            onClick={this.doPost}>
            Post
          </button>
        </div>
      </div>
    )
  }
}
