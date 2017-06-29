import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import {
  BrowserRouter as Router, Link, Route, withRouter, Switch,
} from 'react-router-dom'

import { Blogs, ViewBlog, EditBlog } from './blog'
import Gallery from './Gallery'
import About from './About'
import Files from './Files'

import { fetchJSON, getCurrentUser } from './utils'

import './style.css'

const Nav = ({user}) => {
  return <nav>
    <ul>
      <li><Link to="/">Home</Link></li>
      {/*
      <li><Link to="/blog">Blog</Link></li>
      <li><Link to="/gallery">Gallery</Link></li>
      <li><Link to="/book">Book</Link></li>
      <li><Link to="/movie">Movie</Link></li>
      */}
      <li><Link to="/about">About</Link></li>
      {user && <li>|</li>}
      {user && <li><Link to="/files">Files</Link></li>}
    </ul>
  </nav>
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
    }
  }

  render() {
    return (
      <div id="root-page">
        <Header user={this.state.user}/>
        <main id="main">
          <Switch>
            <Route exact path="/" render={() => 
              <Blogs owner="fans656" user={this.state.user}/>
            }/>
            <Route exact path="/about" component={About}/>
            <Route exact path="/login" component={Login}/>
            <Route exact path="/register" component={Register}/>
            <Route exact path="/gallery" component={Gallery}/>

            {/* ---------------------------------------------- blog */}
            {/* blogs */}
            <Route exact path="/blog" render={() => 
              <Blogs owner="fans656" user={this.state.user}/>
            }/>

            {/* post blog */}
            <Route exact path="/new-blog" render={() => <EditBlog/>}/>

            {/* view blog */}
            <Route exact path="/blog/:id_or_ref" render={({match}) => 
              <ViewBlog id={match.params.id_or_ref}/>
            }/>

            {/* edit blog */}
            <Route exact path="/blog/:id_or_ref/edit" render={({match}) => 
              <EditBlog id={match.params.id_or_ref}/>
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

            {/* ---------------------------------------------- todo page */}
            {/*<Route exact path="*" component={TodoPage}/>*/}
          </Switch>
        </main>
        <footer className="reverse-color">
          <Link to="/">fans656's site</Link>
        </footer>
      </div>
    );
  }

  componentDidMount() {
    getCurrentUser((resp) => {
      this.setState({
        user: !resp.errno ? resp.user : null
      });
    });
  }

  onLogout = () => {
    this.setState({user: null});
    this.props.history.push('/');
  }
}
App = withRouter(App);

const Header = (props) => (
  <header className="reverse-color">
    <Nav user={props.user}/>
    {props.user
      ? <UserName {...props.user}/>
      : <Link to="/login">Login</Link>}
  </header>
);

const UserName = ({username}) => (
  <Link className="username" to={'/profile/' + username}>{username}</Link>
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
            <Link to="/register">
              <button className="secondary">
                  Register
              </button>
            </Link>
            <button onClick={this.doLogin} className="primary">
              Login
            </button>
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

class Profile extends Component {
  doLogout = async () => {
    const res = await fetchJSON('GET', '/api/logout', {
      username: this.props.user.username
    });
    if (!res.errno) {
      this.props.onLogout();
    } else {
      alert('logout failed, see console for details');
      console.log(res);
    }
  }

  render() {
    const user = this.props.user;
    if (!user) {
      return null;
    }
    return (
      <div className="center narrow center-children">
        <h1>{user.username}</h1>
        <button onClick={this.doLogout}>Logout</button>
      </div>
    );
  }
}
Profile = withRouter(Profile);

//const TodoPage = (props) => {
//  const url = props.match.url;
//  console.log(url);
//  return <div style={{
//    fontSize: '1em',
//    display: 'flex',
//    justifyContent: 'center',
//    alignItems: 'center',
//    minHeight: '70vh',
//  }}>
//    <div style={{textAlign: 'center'}}>
//      <h1>404</h1>
//      <p>oops, page not found</p>
//    </div>
//  </div>
//}

ReactDOM.render((
  <Router>
    <Route path="/" component={App}/>
  </Router>
), document.getElementById('root'));
