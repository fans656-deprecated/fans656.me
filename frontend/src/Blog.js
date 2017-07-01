import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import IconPlus from 'react-icons/lib/fa/plus'
import IconCaretLeft from 'react-icons/lib/fa/caret-left'
import IconCaretRight from 'react-icons/lib/fa/caret-right'
import IconEdit from 'react-icons/lib/md/mode-edit'
import qs from 'qs'
import $ from 'jquery'

import Comments from './Comments'
import { Icon, DangerButton, Textarea, Input } from './common'
import { fetchJSON, fetchData } from './utils'

export default class Blog extends Component {
  render() {
    const blog = this.props.blog;
    return <div className="blog">
      <Title className="title" text={blog.title}/>
      <ReactMarkdown className="blog-content" source={blog.content}/>
      <Footer
        blog={blog}
        user={this.props.user}
        isOwner={this.props.isOwner}
        commentsVisible={this.props.commentsVisible}
        isSingleView={this.props.isSingleView}
      />
    </div>
  }
}

const Title = (props) => (
  props.text ? <h2>{props.text}</h2> : null
);

class Footer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      commentsVisible: this.props.commentsVisible || false,
      numComments: this.props.blog.n_comments || 0,
    };
  }

  onCommentsChange = (comments) => {
    if (this.state.numComments != comments.length) {
      this.setState({numComments: comments.length});
    }
    //this.setState(prevState => {
    //  if (prevState.numComments != comments.length) {
    //    return {numComments: comments.length};
    //  } else {
    //    return null;
    //  }
    //});
  }

  toggleCommentsVisible = () => {
    this.setState(prevState => ({
      commentsVisible: !prevState.commentsVisible
    }))
  }

  render() {
    const blog = this.props.blog;
    const ctime = new Date(blog.ctime).toLocaleDateString()
    const tags = (blog.tags || []).map((tag, i) => {
      return <a className="tag info"
        key={i}
        href={`/blog?tags=[${tag}]`}
      >
        {tag}
      </a>
    });

    return (
      <div className="footer">
        <div className="info-row">
          <CommentsToggle
            commentsVisible={this.state.commentsVisible}
            onClick={this.toggleCommentsVisible}
            numComments={this.state.numComments}
            isSingleView={this.props.isSingleView}
          />
          <div className="right">
            <div className="tags" style={{marginRight: '1em'}}>{tags}</div>
            <div className="ctime datetime">
              <Link
                className="info"
                to={`/blog/${blog.id}`}
                title={new Date(blog.ctime).toLocaleString()}
              >{ctime}</Link>
            </div>
            {this.props.isOwner &&
                <a
                  className="edit-blog-link info"
                  href={`/blog/${blog.id}/edit`
                      + (this.props.isSingleView ? '?back-to-single-view=1' : '')
                  }
                  title={`Edit blog ${blog.id}`}
                >
                  <Icon type={IconEdit} size="small"
                    className="blog-edit-icon"
                  />
                </a>
            }
          </div>
        </div>
        {this.props.isSingleView && <br/>}
        <Comments
          visible={this.state.commentsVisible}
          user={this.props.user}
          blog={this.props.blog}
          onChange={this.onCommentsChange}
          isOwner={this.props.isOwner}
        />
      </div>
    )
  }
}

const CommentsToggle = (props) => {
  let infoClassName = '';
  if (props.isSingleView || !props.commentsVisible) {
    infoClassName = 'info';
  }
  return (
    <div>
      <div className={'comments ' + infoClassName}>
        <div className="clickable"
          onClick={props.onClick}
        >
          <a href="#number-of-comments" className="number"
            onClick={ev => ev.preventDefault()}
          >
            {props.numComments}&nbsp;
          </a>
          <span>Comments</span>
        </div>
      </div>
    </div>
  )
}
