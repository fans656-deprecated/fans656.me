import React, { Component } from 'react'
import {
  NORMAL_ICON_SIZE, LARGE_ICON_SIZE, SMALL_ICON_SIZE
} from './constants'
import { excludedSpread } from './utils'

export const Icon = (props) => {
  let size = NORMAL_ICON_SIZE;
  if (props.size === 'small') {
    size = SMALL_ICON_SIZE;
  } else if (props.size === 'large') {
    size = LARGE_ICON_SIZE;
  }
  return React.createElement(props.type, {...props, size: size});
};

export class DangerButton extends Component {
  constructor(props) {
    super(props);
    this.state = {
      clicked: false,
    };
  }

  onClick = () => {
    this.setState(prevState => {
      if (prevState.clicked) {
        this.props.onClick();
      }
      return {
        clicked: !prevState.clicked,
      };
    });
  }

  render() {
    return (
      <button
        className={'danger-button ' + (this.state.clicked ? 'dangerous' : '')}
        onClick={this.onClick}
      >
        {this.props.children}
      </button>
    )
  }
}

export class Textarea extends Component {
  onKeyDown = (ev) => {
    // ctrl-enter
    if (ev.ctrlKey && ev.keyCode === 13) {
      if (this.props.submit) {
        this.props.submit();
      }
    }
  }

  val = () => {
    return this.ref.value;
  }

  clear = () => {
    this.ref.value = null;
  }

  render() {
    return (
      <textarea
        {...excludedSpread(this.props, ['submit'])}
        onKeyDown={this.onKeyDown}
        ref={ref => this.ref = ref}
      >
        {this.props.children}
      </textarea>
    )
  }
}

export class Input extends Component {
  onKeyDown = (ev) => {
    // ctrl-enter
    if (ev.ctrlKey && ev.keyCode === 13) {
      if (this.props.submit) {
        this.props.submit();
      }
    }
  }

  val = () => {
    return this.ref.value;
  }

  clear = () => {
    this.ref.value = null;
  }

  render() {
    return (
      <input
        {...excludedSpread(this.props, ['submit'])}
        onKeyDown={this.onKeyDown}
        ref={ref => this.ref = ref}
      />
    )
  }
}
