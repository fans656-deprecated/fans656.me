import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import IconCaretLeft from 'react-icons/lib/fa/caret-left'
import IconCaretRight from 'react-icons/lib/fa/caret-right'
import IconPlus from 'react-icons/lib/md/add'
import IconSearch from 'react-icons/lib/md/search'
import qs from 'qs'
import $ from 'jquery'

import Blog from './Blog'
import { Icon, DangerButton, Textarea, Input } from './common'
import { fetchJSON, fetchData } from './utils'

export default class Console extends Component {
  constructor(props) {
    super(props);
    this.state = {
      text: '',
      focus: false,
    };
  }

  componentDidMount() {
    const input = $('#console-input');
    const icon = $('#console > svg');
    icon.addClass('info');
    input.focus(() => {
      icon.removeClass('info');
      this.setState({focus: true});
    });
    input.focusout(() => {
      icon.addClass('info');
      this.setState({focus: false});
    });
  }

  onTextChange = ({target}) => {
    const text = target.value;
    this.setState(prevState => {
      const prevText = prevState.text;
      console.log(text);
      return {text: text};
    });
  }

  render() {
    return (
      <div id="console" style={{
        marginRight: '3rem',
      }}>
        <Icon type={IconSearch} size="small"/>
        <input
          id="console-input"
          type="text"
          value={this.state.text}
          title="Type ? for help"
          onChange={this.onTextChange}
        />
      </div>
    );
  }
}
