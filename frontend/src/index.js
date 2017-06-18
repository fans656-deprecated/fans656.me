import React, { Component } from 'react'
import ReactDOM from 'react-dom'

import {
  BrowserRouter as Router, Link, Route, withRouter
} from 'react-router-dom'

import { Editor, Plain } from 'slate'

import IconGithub from 'react-icons/lib/go/mark-github'

import { Blog, Blogs, ViewBlog, EditBlog } from './blog'

import { getDateDiff, fetchJSON, getCurrentUser } from './utils'
import {
  NORMAL_ICON_SIZE, LARGE_ICON_SIZE, SMALL_ICON_SIZE
} from './constants'

import './style.css'
import * as avatarJPG from './avatar.jpg'

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
      <li key="blog"><Link to="/blog">Blog</Link></li>
      <li key="about"><Link to="/about">About</Link></li>
    </ul>
  </nav>
);

const UserName = ({username}) => (
  <Link className="username" to={'/profile/' + username}>{username}</Link>
);

const Icon = (props) => {
  let size = NORMAL_ICON_SIZE;
  if (props.size === 'small') {
    size = SMALL_ICON_SIZE;
  } else if (props.size === 'large') {
    size = LARGE_ICON_SIZE;
  }
  return React.createElement(props.type, {size: size});
};

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
      <div className="center narrow" style={{
        textAlign: 'center',
        marginTop: '50px',
      }}>
        <img src={avatarJPG} width="200px" alt="fans656"/>
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
          <div className="links" style={{
            display: 'flex',
            justifyContent: 'center',
          }}>
            <a className="icon" href="https://github.com/fans656">
              <Icon type={IconGithub}/>
              &nbsp;&nbsp;{'github.com/fans656'}
            </a>
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
    if (res.errno) {
      alert(res.detail);
    } else {
      window.location.href = '/';
    }
  }

  render() {
    return (
      <div className="center narrow center-children" style={{marginTop: '10%'}}>
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
          <button onClick={this.doLogin}>Login</button>
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
    if (!this.props.user) {
      return null;
    }
    return (
      <div className="center narrow center-children">
        <button onClick={this.doLogout}>Logout</button>
      </div>
    );
  }
}
Profile = withRouter(Profile);

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
        user: !resp.errno ? resp.user : null
      });
      console.log('getCurrentUser:');
      console.log(resp);
    });
  }

  onLogout = () => {
    this.setState({user: null});
    this.props.history.push('/');
  }

  render() {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh'
      }}>
        <Header user={this.state.user}/>
        <main>
          <Route exact path="/" render={() =>
            <h1>Home todo</h1>
          }/>
          <Route path="/about" component={About}/>
          <Route path="/login" component={Login}/>

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
        </main>
        <footer className="reverse-color">
          <Link to="/">fans656's site</Link>
        </footer>
      </div>
    );
  }
}
App = withRouter(App);

ReactDOM.render((
  <Router>
    <Route path="/" component={App}/>
  </Router>
), document.getElementById('root'));
