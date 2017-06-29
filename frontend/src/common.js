import React, { Component } from 'react'
import {
  NORMAL_ICON_SIZE, LARGE_ICON_SIZE, SMALL_ICON_SIZE
} from './constants'

export const Icon = (props) => {
  let size = NORMAL_ICON_SIZE;
  if (props.size === 'small') {
    size = SMALL_ICON_SIZE;
  } else if (props.size === 'large') {
    size = LARGE_ICON_SIZE;
  }
  return React.createElement(props.type, {size: size});
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
