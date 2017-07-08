import React, { Component } from 'react'
import qs from 'qs'
import $ from 'jquery'

import { fetchData } from './utils'

export default class Reader extends Component {
  constructor(props) {
    super(props);
    this.loading = false;
    this.state = {
      content: props.content,
      search: [],
      initialOffset: parseInt(props.options.offset) || 0,
    };
  }

  componentDidMount() {
    this.props.registerConsoleHandler(this.consoleHandler);
    // scroll down to load
    $(document).scroll(this.onscroll);
    // scroll up to load
    $(document).keydown(this.onkeydown);
  }

  onscroll = ev => {
    const body = $('body');
    const maxScrollY = body.prop('scrollHeight') - body.outerHeight();
    const percentage = window.scrollY / maxScrollY;
    if ((1 - percentage) * this.state.content.length < 500
      && !this.loading && this.state.search.length === 0) {
      this.loading = true;

      const options = this.props.options;
      const initialOffset = this.state.initialOffset;
      const size = options.size;

      let url = this.props.url + '?offset='
        + (initialOffset + this.state.content.length);
      fetchData('GET', url, res => {
        this.loading = false;
        this.setState(prevState => {
          return {
            content: prevState.content + res.content,
          }
        });
      });
    }
  }

  onkeydown = ev => {
    if ((ev.key === 'ArrowUp' || ev.key === 'PageUp') && window.scrollY === 0) {
      this.loadPrevContent();
    }
  }

  loadPrevContent = () => {
    if (this.loading) {
      return;
    }
    this.loading = true;

    const options = this.props.options;
    const initialOffset = this.state.initialOffset;
    const size = Math.min(100, options.size);
    const offset = Math.max(0, initialOffset - size);

    let url = this.props.url + '?offset=' + offset;
    fetchData('GET', url, res => {
      this.loading = false;
      const prevContent = res.content.substring(0, initialOffset - offset);
      this.setState(prevState => {
        return {
          content: prevContent + prevState.content,
          initialOffset: offset,
        }
      });
    });
  }

  componentWillUnmount() {
    $(document).unbind('scroll', this.onscroll);
    $(document).unbind('keydown', this.onkeydown);
    $(document).unbind('mousewheel', this.onmousewheel);
    clearInterval(this.timer);
  }

  consoleHandler = ({type, data: text}) => {
    if (type !== 'enter') {
      return;
    }
    if (text.length === 0) {
      this.setState({search: []});
    } else {
      fetchData('GET', this.props.url + '?' + 'search=' + text, res => {
        this.setState({search: res.occurrences});
      });
    }
  }

  render() {
    if (this.state.search.length > 0) { 
      return <div className="reader">
        {this.state.search.map((occurrence, i) => {
          const pattern = occurrence.pattern;
          const text = occurrence.context;
          const offset = occurrence.contextOffset;
          const pre = text.substring(0, offset);
          const patternText = text.substring(offset, offset + pattern.length);
          const after = text.substring(offset + pattern.length, text.length);
          return (
            <div key={occurrence.offset}>
              {i !== 0 && <hr/>}
              <p className="read-search-result" onClick={() => {
                window.location.href = 
                  window.location.origin + window.location.pathname
                  + '?offset=' + Math.max(0, occurrence.offset - 100);
              }}>
                {pre}
                <strong>{patternText}</strong>
                {after}
              </p>
            </div>
          )
        })}
      </div>
    }

    const options = this.props.options;
    const initialOffset = this.state.initialOffset;
    const pageSize = parseInt(options.size || 1000);

    const content = this.state.content;
    const lines = content.split('\n');
    let offset = initialOffset
      ? initialOffset
      : (this.initialPage - 1) * pageSize;
    let page = null;

    const paragraphs = [];
    for (let i = 0; i < lines.length; i++) {
      let curPage = Math.floor(offset / pageSize);
      let showPage = false;
      if (curPage != page) {
        showPage = true;
        page = curPage;
      }

      paragraphs.push(
        <div key={i}>
          <p className="reader-paragraph">
            {lines[i].replace(/ /g, '\u00a0')}
          </p>
        </div>
      );
      offset += lines[i].length + 1;
    }
    const attrs = this.props.attrs;
    return <div className="reader">
        <div>
          <h1 style={{textAlign: 'center'}}>{this.props.name}</h1>
          {attrs.author && <p style={{textAlign: 'right'}}>{attrs.author}</p>}
        </div>
      {initialOffset !== 0 && <p style={{
        color: '#aaa',
        fontSize: '.8em',
        textAlign: 'center',
        cursor: 'pointer',
      }} onClick={this.loadPrevContent}
      >...{initialOffset} more chars (scroll up to see)</p>}
      <div className="paragraphs">
        {paragraphs}
      </div>
    </div>
  }
}
