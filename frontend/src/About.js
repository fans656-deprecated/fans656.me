import React, { Component } from 'react'
import IconGithub from 'react-icons/lib/go/mark-github'

import { Icon } from './common'

import { getDateDiff } from './utils'

export default class About extends Component {
  constructor(props) {
    super(props);
    this.birth = new Date('1989-12-12T01:06:56');
    this.state = {
      now: new Date(),
    };
  }
  
  componentDidMount() {
    this.timerId = setInterval(() => this.setState({now: new Date()}), 1000);
  }
  
  componentWillUnmount() {
    clearInterval(this.timerId);
  }

  render() {
    const [years, months, days, hours, minutes, seconds] = getDateDiff(
        this.birth, this.state.now);
    return (
      <div>
        <div className="about">
          <img className="large avatar" src="/file/fans656.jpg" alt="fans656"/>
          <p className="nickname">fans656</p>
          <p style={{fontSize: '0.4em'}}> is up running for </p>
          <div className="age">
            <div>
              <span className="num years">{years}</span>
              <span className="unit">yr</span>
              <span className="num months">{months}</span>
              <span className="unit">mos</span>
              <span className="num days">{days}</span>
              <span className="unit">days</span>
            </div>
            <div>
              <span className="num hours">{hours}</span>
              <span className="unit">hr</span>
              <span className="num minutes">{minutes}</span>
              <span className="unit">min</span>
              <span className="num seconds">{Math.floor(seconds)}</span>
              <span className="unit">secs</span>
            </div>
          </div>
          <div className="hr"/>
          <div className="links" style={{
            display: 'flex',
            justifyContent: 'center',
          }}>
            <a className="icon"
              href="https://github.com/fans656"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Icon type={IconGithub}/>
              &nbsp;&nbsp;{'github.com/fans656'}
            </a>
          </div>
        </div>
      </div>
    );
  }
}
