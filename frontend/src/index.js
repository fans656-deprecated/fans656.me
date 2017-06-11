import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Link, Route } from 'react-router-dom';
import './style.css';

import { articles } from './content';
import { getDateDiff } from './utils';

const Header = () => (
  <header className="reverse-color">
    <Nav/>
    <UserInfo/>
  </header>
);

const Nav = () => (
  <nav>
    <ul>
      <li key="home"><Link to="/">Home</Link></li>
      {/*
      <li key="blog"><Link to="/blog">Blog</Link></li>
      <li key="apps"><Link to="/apps">Apps</Link></li>
      */}
      <li key="about"><Link to="/about">About</Link></li>
    </ul>
  </nav>
);

const UserInfo = () => (
  <div className="login">
    <p>Login</p>
  </div>
);

const Articles = () => (
  <div>{articles.slice(0,999)}</div>
);

class About extends Component {
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
      <div style={{textAlign: 'center'}}>
        <img src="https://avatars2.githubusercontent.com/u/1287428?v=3&s=240"/>
        <div className="about">
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
          <hr/>
        </div>
      </div>
    );
  }
}

const Todo = () => (
  <div className="todo">
    <h1>To be complete</h1>
  </div>
);

class App extends React.Component {
  render() {
    return (
      <Router>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh'
        }}>
          <Header/>
          <main>
            <Route exact path="/" component={Articles}/>
            <Route path="/about" component={About}/>
          </main>
          <footer className="reverse-color">fans656's site</footer>
        </div>
      </Router>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));
