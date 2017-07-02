import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import IconEdit from 'react-icons/lib/md/mode-edit'
import IconLink from 'react-icons/lib/md/link'
import qs from 'qs'
import $ from 'jquery'

import Comments from './Comments'
import { Icon } from './common'

export default class Blog extends Component {
  render() {
    const blog = this.props.blog;
    return <div className="blog">
      <Title className="title" text={blog.title}/>
      <ReactMarkdown className="blog-content" source={blog.content}/>
      <Footer
        blog={blog}
        user={this.props.user}
        commentsVisible={this.props.commentsVisible || this.props.isSingleView}
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
    if (this.state.numComments !== comments.length) {
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
      let url = `/blog?${qs.stringify({tags: [tag]})}`;
      return <a className="tag info"
        key={i}
        href={url}
      >
        {tag}
      </a>
    });

    return (
      <div className="footer">
        <div className="info-row info">
          <div className="column left">
            <CommentsToggle
              commentsVisible={this.state.commentsVisible}
              onClick={this.toggleCommentsVisible}
              numComments={this.state.numComments}
              isSingleView={this.props.isSingleView}
            />
            {blog.custom_url &&
              <a className="custom-url filter"
                href={blog.custom_url}
                title={`Custom URL ${window.location.origin}${blog.custom_url}`}
              >
                <Icon type={IconLink} size="small"/>
              </a>
            }
          </div>
          <div className="column right">
            <div className="tags filter" style={{marginRight: '1em'}}>{tags}</div>
            <div className="ctime datetime filter">
              <Link
                to={`/blog/${blog.id}`}
                title={new Date(blog.ctime).toLocaleString()}
              >{ctime}</Link>
            </div>
            {this.props.user.isOwner() &&
                <a
                  className="edit-blog-link filter"
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
        <Comments
          visible={this.state.commentsVisible}
          user={this.props.user}
          blog={this.props.blog}
          onChange={this.onCommentsChange}
        />
      </div>
    )
  }
}

class CommentsToggle extends Component {
  componentWillReceiveProps(props) {
    if (props.isSingleView || props.commentsVisible) {
      $('.comments.toggle').addClass('toggled');
    } else {
      $('.comments.toggle').removeClass('toggled');
    }
  }

  render() {
    return (
      <div>
        <div className="comments toggle filter">
          <div className="clickable"
            onClick={this.props.onClick}
          >
            <a href="#number-of-comments" className="number"
              onClick={ev => ev.preventDefault()}
            >
              {this.props.numComments}&nbsp;
            </a>
            <span>Comments</span>
          </div>
        </div>
      </div>
    )
  }
}
