import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Link, Route } from 'react-router-dom';

import IconGithub from 'react-icons/lib/go/mark-github';

import { articles } from './content';
import { getDateDiff, fetchJSON, getCurrentUser } from './utils';

import './style.css';
import * as avatarJPG from './avatar.jpg';

const Header = (props) => (
  <header className="reverse-color">
    <Nav/>
    {props.user
      ? <UserName {...props.user}/>
      : <Link to="/login">Login</Link>}
  </header>
);

const Nav = () => (
  <nav>
    <ul>
      <li key="home"><Link to="/">Home</Link></li>
      <li key="about"><Link to="/about">About</Link></li>
    </ul>
  </nav>
);

const UserName = ({username}) => (
  <Link className="username" to={'/profile/' + username}>{username}</Link>
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
        <img src={avatarJPG} width="200px"/>
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
          <div className="links">
            <IconGithub size={20} />
            <Link to="https://github.com/fans656">
              {'github.com/fans656'}
            </Link>
          </div>
        </div>
      </div>
    );
  }
}

class Login extends Component {
  doLogin = async (ev) => {
    ev.preventDefault();
    const res = await fetchJSON('POST', '/api/login', {
      username: this.username.value,
      password: this.password.value,
    });
    if (!res.ok) {
      alert(res.detail);
    } else {
      window.location.href = '/';
    }
  }

  render() {
    return (
      <form className="login" onSubmit={this.doLogin}>
        <input name="username"
          defaultValue="a"
          placeholder="Username"
          ref={input => this.username = input}
        />
        <input name="password"
          defaultValue="b"
          placeholder="Password" type="password"
          ref={input => this.password = input}
        />
        <a href="" onClick={this.doLogin}>Login</a>
        <input style={{display: 'none'}} type="submit"/>
      </form>
    );
  }
}

class Profile extends Component {
  
  doLogout = async () => {
    const resp = await fetchJSON('GET', '/api/logout', {
      username: this.props.user.username
    });
    if (resp.ok) {
      window.location.href = '/';
    } else {
      console.log(resp);
      alert('logout failed, see console for details');
    }
  }

  render() {
    if (!this.props.user) {
      return null;
    }
    return (
      <a href="" onClick={(ev) => {ev.preventDefault(); this.doLogout()}}>Logout</a>
    );
  }
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
    }
  }

  componentDidMount() {
    getCurrentUser((resp) => {
      this.setState({
        user: resp.ok ? resp.user : null
      });
      console.log('getCurrentUser:');
      console.log(resp);
    });
  }

  render() {
    return (
      <Router>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh'
        }}>
          <Header user={this.state.user}/>
          <main>
            <Route exact path="/" component={Articles}/>
            <Route path="/about" component={About}/>
            <Route path="/login" component={Login}/>
            <Route path="/profile/:username" render={
              (props) => <Profile user={this.state.user} {...props}/>
            }/>
          </main>
          <footer className="reverse-color"><Link to="/">fans656's site</Link></footer>
        </div>
      </Router>
    );
  }
}

ReactDOM.render((
  <App />
), document.getElementById('root'));
