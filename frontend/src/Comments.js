import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import IconDelete from 'react-icons/lib/md/delete'

import { Icon, Textarea } from './common'
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
    const url =  `/api/blog/${blog.id}/comment`;
    fetchData('GET', url, ({comments}) => {
      this.setState({comments: comments});
      this.props.onChange(comments);
    });
  }

  render() {
    if (!this.props.visible) {
      return null;
    }
    const comments = this.state.comments.map((comment, i) => {
      return <Comment
        key={i}
        comment={comment}
        username={comment.username}
        user={this.props.user}
        isVisitor={comment.is_visitor}
        ctime={comment.ctime}
        content={comment.content}
        onDelete={this.fetchComments}
      />
    });
    return <div className="comments-content">
      {comments}
      <CommentEdit
        user={this.props.user}
        blog={this.props.blog}
        onChange={this.fetchComments}
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

  doDelete = () => {
    const url = `/api/comment/${this.props.comment.id}`;
    fetchData('DELETE', url, this.props.onDelete);
  }

  render() {
    const comment = this.props.comment;
    const ctime = new Date(this.props.ctime);
    return (
      <div className="comment"
        style={{
          paddingBottom: '1em',
          display: 'block',
        }}
      >
        <div className="comment-header" style={{
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
          <span className="info" style={{marginLeft: 'auto',}}>
            <span className="datetime filter">
              {ctime.toLocaleString()}
            </span>
            {this.props.user.isOwner() &&
              <a className="hover-action delete-comment filter"
                style={{
                  position: 'relative',
                  top: '-0.1rem',
                  left: '0.5rem',
                }}
                onClick={ev => {
                  ev.preventDefault();
                  this.doDelete();
                }}
                title={`Delete comment ${comment.id}`}
              >
                <Icon type={IconDelete} size="small"/>
              </a>
            }
          </span>
        </div>
        <div className="comment-content">
          {comment.content.split('\n').map((line, i) =>
            <p key={i} style={{margin: '0'}}>{line}</p>)
          }
        </div>
      </div>
    )
  }
}


class CommentEdit extends Component {
  doPost = async () => {
    const content = this.textarea.val();
    if (content.length === 0) {
      alert('Empty?');
      return;
    }
    let comment = {
      content: content,
    };
    const user = this.props.user;
    if (user.isLoggedIn()) {
      comment.user = user;
    } else {
      comment.visitorName = this.nameInput.value;
    }

    const blog = this.props.blog;
    const url = `/api/blog/${blog.id}/comment`;
    fetchData('POST', url, comment, () => {
      this.props.onChange();
      this.textarea.clear();
    });
  }

  render() {
    const user = this.props.user;
    return (
      <div>
        <Textarea
          className="comment-edit"
          placeholder="Write your comment here..."
          submit={this.doPost}
          onKeyUp={({target}) => {
            target.style.height = '5px';
            target.style.height = target.scrollHeight + 15 + 'px';
          }}
          style={{
            boxSizing: 'border-box',
          }}
          ref={ref => this.textarea = ref}
        >
        </Textarea>
        <div style={{
          display: 'flex',
          //justifyContent: 'flex-end',
          width: '100%',
        }}>
          {!user.isLoggedIn() &&
            <div className="vistor-name-input-and-post-button">
              <input className="visitor-name"
                style={{
                  padding: '0 .4rem',
                }}
                type="text"
                placeholder="Who are you?"
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
