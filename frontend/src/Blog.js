import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import IconEdit from 'react-icons/lib/md/mode-edit'
import IconLink from 'react-icons/lib/md/link'
import IconBook from 'react-icons/lib/fa/book'
import qs from 'qs'
import $ from 'jquery'

import Comments from './Comments'
import Reader from './Reader'
import Gallery from './Gallery'
import LeetcodeStatistics from './LeetcodeStatistics'
import { Icon } from './common'
import { fetchData } from './utils'

export default class Blog extends Component {
  constructor(props) {
    super(props);

    this.state = {
      replaceContent: null
    };
  }

  parse = blog => {
    if (blog.leetcode) {
      let leetcode;
      try {
        leetcode = JSON.parse(blog.leetcode);
      } catch (e) {
        console.log(e);
        return;
      }
      const title = $(`<a href="${leetcode.url}"/>`)
        .append($(`<h2>Leetcode ${leetcode.title}</h2>`));
      const description = $(leetcode.description);
      this.preContent = title;
      this.afterContent = $('<div/>')
        .append($(`<a href="${leetcode.url}"><h2>Original Problem:</h2></a>`))
        .append(description);
    } else if (blog.type === 'txt') {
      // book read mode
      if (this.props.isSingleView) {
        let options = {
          page: 1,
          size: 1000,
          offset: 0,
          ...qs.parse(window.location.search.slice(1)),
        };
        let url = '/api/read/' + blog.id + window.location.search;
        fetchData('GET', url, res => {
          this.setState({
            replaceContent: (
              <Reader
                name={res.name}
                attrs={JSON.parse(res.attrs)}
                url={'/api/read/' + blog.id}
                options={options}
                content={res.content}
                registerConsoleHandler={this.props.registerConsoleHandler}
              />
            ),
            replaceAll: true,
          });
        });
      // blog entry mode
      } else {
        fetchData('GET', '/api/read/' + blog.id, res => {
          const url = blog.custom_url || `/blog/${blog.id}`;
          const attrs = JSON.parse(res.attrs);
          const replaceContent = (
            <div>
              <div>
                <a href={url} style={{
                  fontWeight: 'bold',
                  fontSize: '1.1rem',
                }}>
                  <Icon type={IconBook} style={{
                    position: 'relative',
                    top: '-2px',
                  }}/>
                  <span style={{
                    marginLeft: '.5rem',
                  }}>
                    {res.name}
                  </span>
                  <span style={{
                    margin: '0 .5rem',
                  }}>-</span>
                  <span>
                    {attrs.author}
                  </span>
                </a>
              </div>
              {blog.description && <div style={{
                marginTop: '1rem',
              }}>
                <ReactMarkdown className="blog-content"
                  source={blog.description}
                />
              </div>
              }
            </div>
          );
          this.setState({
            replaceContent: replaceContent,
            replaceAll: false,
          });
        });
      }
    // JSON
    } else if (blog.content.substring(0, 2) === '{\n') {
      const lines = blog.content.split('\n');
      const iJsonEndLine = lines.indexOf('}');
      if (iJsonEndLine === -1) {
        return;
      }
      const jsonStr = lines.slice(0, iJsonEndLine + 1).join('\n');
      const json = JSON.parse(jsonStr);
      const content = lines.slice(iJsonEndLine + 1, lines.length).join('\n');
      if (json.type === 'gallery') {
        this.setState({
          replaceContent: (
            <div>
              <Gallery json={json}
                viewtype={this.props.isSingleView ? 'page' : 'item'}
                blogURL={blog.custom_url || '/blog/' + blog.id}
              />
              <ReactMarkdown className="blog-content"
                source={content}
              />
            </div>
          ),
          replaceAll: this.props.isSingleView,
        });
      } else if (json.type === 'only-single-view') {
        if (this.props.isSingleView) {
          this.setState({
            replaceContent: (
              <ReactMarkdown className="blog-content"
                source={content}
              />
            ),
          });
        } else {
          this.setState({
            replaceContent: (
              <ReactMarkdown className="blog-content"
                source={json.placeholder}
              />
            ),
          });
        }
      } else if (json.type === 'leetcode-statistics') {
        this.setState({
          replaceContent: <div>
            <ReactMarkdown className="blog-content"
              source={content}
            />
            <LeetcodeStatistics
              title={json.title}
              content={content}
              isSingleView={this.props.isSingleView}
            />
          </div>
        });
      }
    }
  }

  componentDidMount() {
    this.parse(this.props.blog);

    const blog = this.props.blog;
    $(`.blog#${blog.id} .pre-content`).append(this.preContent);
    $(`.blog#${blog.id} .after-content`).append(this.afterContent);
  }

  render() {
    const blog = this.props.blog;
    if (this.state.replaceAll) {
      return this.state.replaceContent;
    }
    const className = this.props.isSingleView ? 'single-blog-view' : ''
    return <div className={'blog ' + className} id={blog.id}>
      <Title className="title" text={blog.title}/>
      <div className="pre-content"/>
      {this.state.replaceContent ? this.state.replaceContent :
      <ReactMarkdown className="blog-content" source={blog.content}/>
      }
      <div className="after-content"/>
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
            <div className="tags filter" style={{marginRight: '1em'}}>
              {tags}
            </div>
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
  componentDidMount() {
    this.syncCommentsToggleState(this.props);
  }

  componentWillReceiveProps(props) {
    this.syncCommentsToggleState(props);
  }

  syncCommentsToggleState = props => {
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
