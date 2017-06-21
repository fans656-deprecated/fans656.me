import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import {
  BrowserRouter as Router, Link, Route, withRouter
} from 'react-router-dom'

import Gallery from './gallery'
import About from './about'
import { Blogs, ViewBlog, EditBlog } from './blog'
import { fetchJSON, getCurrentUser } from './utils'

import './style.css'

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
          <Route path="/gallery" component={Gallery}/>

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
      <li key="gallery"><Link to="/gallery">Gallery</Link></li>
      <li key="about"><Link to="/about">About</Link></li>
    </ul>
  </nav>
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

ReactDOM.render((
  <Router>
    <Route path="/" component={App}/>
  </Router>
), document.getElementById('root'));
