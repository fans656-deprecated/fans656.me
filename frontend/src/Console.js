import React, { Component } from 'react'
import IconSearch from 'react-icons/lib/md/search'
import $ from 'jquery'

import { Icon } from './common'
import installMatrix from './matrix'

export default class Console extends Component {
  constructor(props) {
    super(props);
    this.state = {
      text: '',
      focus: false,
    };
    this.typeEaseTimer = null;
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
      //const prevText = prevState.text;
      return {text: text};
    }, () => {
      if (this.typeEaseTimer) {
        clearTimeout(this.typeEaseTimer);
        this.typeEaseTimer = null;
      }
      this.typeEaseTimer = setTimeout(this.onTypeEase, 500);
    });
  }

  onTypeEase = (type) => {
    clearTimeout(this.typeEaseTimer);
    this.typeEaseTimer = null;

    const text = this.state.text;
    if (text === '  matrix') {
      installMatrix();
      return;
    }
    const event = new Event({
      type: type || 'typeEase',
      data: text,
      accepted: false,
    });
    for (const handler of this.props.handlers) {
      try {
        handler(event);
        if (event.accepted) {
          break;
        }
      } catch (e) {
        event.accepted = false;
      }
    }
    return;
  }

  onKeyUp = ev => {
    if (ev.key === 'Enter') {
      this.onTypeEase('enter');
    }
  }

  render() {
    const hasHandlers = this.props.handlers.length !== 0;
    return (
      <div id="console" style={{
        marginRight: '3rem',
        visibility: hasHandlers ? 'visible' : 'hidden',
      }}>
        <Icon type={IconSearch} size="small"/>
        <input
          id="console-input"
          type="text"
          value={this.state.text}
          title="Type ? for help"
          onChange={this.onTextChange}
          onKeyUp={this.onKeyUp}
        />
      </div>
    );
  }
}

class Event {
  constructor(props) {
    this.type = props.type;
    this.data = props.data;
    this.accepted = false;
  }

  accept = () => {
    this.accepted = true;
  }
}
