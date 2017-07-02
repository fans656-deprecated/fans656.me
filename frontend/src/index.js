import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import {
  BrowserRouter as Router, Link, Route, withRouter, Switch,
} from 'react-router-dom'
import $ from 'jquery'

import Blog from './Blog'
import Blogs, { ViewBlog, EditBlog } from './Blogs'
import Console from './Console'
import Profile from './Profile'
import Gallery from './Gallery'
import About from './About'
import Files from './Files'

import { fetchJSON, fetchData, getCurrentUser } from './utils'

import './style.css'

const Nav = ({user}) => {
  return <nav>
    <ul>
      <li><a href="/">Home</a></li>
      {/*
      <li><Link to="/blog">Blog</Link></li>
      <li><Link to="/gallery">Gallery</Link></li>
      <li><Link to="/book">Book</Link></li>
      <li><Link to="/movie">Movie</Link></li>
      */}
      <li><Link to="/about">About</Link></li>
      {user.isMe() && <li>|</li>}
      {user.isMe() && <li><Link to="/files">Files</Link></li>}
    </ul>
  </nav>
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user: new User(),
      consoleHandlers: [],
    }
  }

  keypress = (ev) => {
    const body = $('body');
    if (ev.key === 's' && ev.target === body[0]) {
      $('#console input').focus();
      ev.preventDefault();
      ev.stopPropagation();
    }
  }

  registerConsoleHandler = (handler) => {
    this.setState(prevState => {
      const handlers = prevState.consoleHandlers;
      handlers.push(handler);
      return {
        consoleHandlers: handlers,
      }
    });
  }

  unregisterConsoleHandler = (target_handler) => {
    this.setState(prevState => {
      const handlers = prevState.consoleHandlers;
      for (let i = 0; i < handlers.length; ++i) {
        const handler = handlers[i];
        if (handler === target_handler) {
          handlers.splice(i, 1);
          break;
        }
      }
      return {
        consoleHandlers: handlers,
      }
    });
  }

  render() {
    return (
      <div id="root-page">
        <Header user={this.state.user}
          consoleHandlers={this.state.consoleHandlers}
        />
        <main id="main">
          <Switch>
            <Route exact path="/about" component={About}/>
            <Route exact path="/login" component={Login}/>
            <Route exact path="/register" component={Register}/>
            <Route exact path="/gallery" component={Gallery}/>

            {/* ---------------------------------------------- blog */}
            {/* blogs */}
            <Route exact path="/" render={() => 
                <Blogs user={this.state.user}
                  registerConsoleHandler={this.registerConsoleHandler}
                  unregisterConsoleHandler={this.unregisterConsoleHandler}
                />
            }/>
            <Route exact path="/blog" render={() => 
                <Blogs user={this.state.user}
                  registerConsoleHandler={this.registerConsoleHandler}
                  unregisterConsoleHandler={this.unregisterConsoleHandler}
                />
            }/>

            {/* post blog */}
            <Route exact path="/new-blog" render={() => (
              <EditBlog user={this.state.user}/>
            )}/>

            {/* view blog */}
            <Route exact path="/blog/:id_or_ref" render={({match}) => 
              <ViewBlog
                id={match.params.id_or_ref}
                user={this.state.user}
              />
            }/>

            {/* edit blog */}
            <Route exact path="/blog/:id_or_ref/edit" render={({match}) => 
              <EditBlog id={match.params.id_or_ref} user={this.state.user}/>
            }/>

            {/* profile */}
            <Route path="/profile/:username" render={(props) =>
              <Profile
                user={this.state.user}
                onLogout={this.onLogout}
              />
            }/>

            {/* ---------------------------------------------- personal */}
            <Route path="/files" component={Files}/>

            {/* ---------------------------------------------- custom url */}
            {<Route exact path="*" render={(props) => (
              <CustomURLPage {...props} user={this.state.user}/>
            )}/>}
          </Switch>
        </main>
        <footer className="reverse-color">
          <Link to="/">fans656's site</Link>
        </footer>
      </div>
    );
  }

  componentDidMount() {
    $('body').keypress(this.keypress);
    getCurrentUser(res => {
      const user = new User(res.user);
      user.onChange = () => this.setState({user: user});
      this.setState({user: user});
      //const user = res.errno ? null : res.user;
      //if (user) {
      //  user.onChange = () => this.setState({user: user});
      //}
      //this.setState({
      //  user: user,
      //});
    });
  }

  onLogout = () => {
    this.setState({user: null});
    this.props.history.push('/');
  }
}
App = withRouter(App);

const Header = (props) => {
  return <header className="reverse-color">
    <Nav user={props.user}/>
    <div className="right" style={{
      marginLeft: 'auto',
      display: 'inline-flex',
      alignItems: 'center',
    }}>
      <Console
        style={{
          marginRight: '1em',
        }}
        handlers={props.consoleHandlers}
      />
      <span>
        {props.user
          ? <UserName user={props.user}/>
          : <Link to="/login">Login</Link>}
      </span>
    </div>
  </header>
};

const UserName = ({user}) => (
  <Link className="username" to={'/profile/' + user.username}>
    <div style={{
      display: 'inline-flex',
      alignItems: 'center', }}>
      <img className="avatar" src={user.avatar_url} height="28" style={{
        marginRight: 10,
        borderRadius: 16,
      }} alt=""/>
      <span>{user.username}</span>
    </div>
  </Link>
);

class Login extends Component {
  doLogin = async (ev) => {
    ev.preventDefault();
    const res = await fetchJSON('POST', '/api/login', {
      username: this.username.value,
      password: this.password.value,
    });
    if (res.errno) {
      alert(res.detail);
    } else {
      window.location.href = '/';
    }
  }

  render() {
    return (
      <div className="login-page">
        <form className="dialog" onSubmit={this.doLogin}>
          <h1>Login</h1>
          <input
            type="text"
            name="username"
            placeholder="Username"
            ref={input => this.username = input}
          />
          <input
            type="password"
            name="password"
            placeholder="Password" 
            ref={input => this.password = input}
          />
          <div>
            <button onClick={this.doLogin} className="primary">
              Login
            </button>
            <Link to="/register" style={{float: 'left'}}>
              <button className="secondary">
                  Register
              </button>
            </Link>
          </div>
          <input style={{display: 'none'}} type="submit"/>
        </form>
      </div>
    );
  }
}

class Register extends Component {
  doRegister = async (ev) => {
    ev.preventDefault();
    const username = this.username.value;
    const password = this.password.value;
    const confirmPassword = this.confirmPassword.value;
    if (!username.match(/[-_a-zA-Z0-9]+/)) {
      alert('Invalid username!');
      return;
    }
    if (username.length === 0) {
      alert('Username required!');
      return;
    }
    if (username.length > 255) {
      alert('Username too long!');
      return;
    }
    if (password.length === 0) {
      alert('Password required!');
      return;
    }
    if (password.value !== confirmPassword.value) {
      alert('Password mismatch!');
      return;
    }
    const res = await fetchJSON('POST', '/api/register', {
      username: username,
      password: password,
    });
    if (res.errno) {
      alert(res.detail);
    } else {
      window.location.href = '/';
    }
  }

  render() {
    return (
      <div className="login-page">
        <form className="dialog" onSubmit={this.doRegister}>
          <h1>Register</h1>
          <input
            type="text"
            name="username"
            placeholder="Username"
            ref={input => this.username = input}
          />
          <input
            id="password"
            type="password"
            placeholder="Password" 
            ref={input => this.password = input}
          />
          <input
            id="confirm"
            type="password"
            placeholder="Confirm password" 
            ref={input => this.confirmPassword = input}
          />
          <button onClick={this.doRegister} className="primary">Register</button>
          <input style={{display: 'none'}} type="submit"/>
        </form>
      </div>
    );
  }
}

class CustomURLPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      res: null,
    };
  }

  componentWillReceiveProps(props) {
    const path = props.match.url;
    const setState = res => this.setState({res: res});
    if (path) {
      fetchData('GET', '/api/custom-url' + path, setState, setState);
    }
  }

  render() {
    if (!this.state.res) {
      return null;
    } else {
      const res = this.state.res;
      if (res.errno) {
        return <div style={{
          fontSize: '1em',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '70vh',
        }}>
          <div style={{textAlign: 'center'}}>
            <h1>{res.errno}</h1>
            <p>{res.detail}</p>
          </div>
        </div>
      } else if (res.type === 'blog') {
        return (
          <ViewBlog blog={res.blog} user={this.props.user}/>
        )
      } else {
        return <pre>{res.detail}</pre>
      }
    }
  }
}

class User {
  constructor(user) {
    user = user || {
      username: ''
    };

    Object.assign(this, user);
  }

  valid = () => this.username.length > 0
  isLoggedIn = () => this.valid()
  isMe = () => this.username === 'fans656'
  isOwner = () => this.isMe()
}

ReactDOM.render((
  <Router>
    <Route path="/" component={App}/>
  </Router>
), document.getElementById('root'));
