import React, { Component } from 'react';
import ReactDOM from 'react-dom';

import { createBrowserHistory } from 'history';
import { BrowserRouter as Router, Link, Route } from 'react-router-dom';

import { Editor, Plain } from 'slate';

import IconGithub from 'react-icons/lib/go/mark-github';
import IconTop from 'react-icons/lib/fa/chevron-up';
import IconPlus from 'react-icons/lib/fa/plus';

import { getDateDiff, fetchJSON, getCurrentUser } from './utils';
import { NORMAL_ICON_SIZE, LARGE_ICON_SIZE, SMALL_ICON_SIZE } from './constants';

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

const Icon = (props) => {
  let size = NORMAL_ICON_SIZE;
  if (props.size === 'small') {
    size = SMALL_ICON_SIZE;
  } else if (props.size === 'large') {
    size = LARGE_ICON_SIZE;
  }
  return React.createElement(props.type, {size: size});
};

class Blogs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      blogs: [],
    };
  }
  
  componentDidMount() {
    this.getBlogs();
  }
  
  getBlogs = async () => {
    const title = this.props.title;
    let url = '/api/blog';
    if (title) {
      url += '/' + encodeURIComponent(title);
    }
    const res = await fetchJSON('GET', url, {
      username: this.props.username,
      id: this.props.id,
    });
    if (res.ok) {
      this.setState({blogs: res.blogs});
    }
  }
  
  render() {
    const blogs = this.state.blogs.map((blog) => {
      const paragraphs = blog.content.split('\n');
      return (
        <article key={blog.id}>
          <div className="title">
            {blog.title ? <h1>{blog.title}</h1> : null}
          </div>
          <div className="paragraphs">
            {paragraphs.map(paragraph => <p>{paragraph}</p>)}
          </div>
        </article>
      );
    });
    let sticky;
    if (this.props.user) {
      sticky = (
        <div className="sticky">
          <div className="tooltip-container">
            <Link to="/new-blog"><Icon type={IconPlus}/></Link>
            <div className="tooltip reverse-color">New blog</div>
          </div>
        </div>
      );
    }
    return (
      <div className="center narrow">
        <div className="blogs">
          {blogs}
        </div>
        {sticky}
      </div>
    );
  }
}

class NewBlog extends Component {
  constructor(props) {
    console.log('NewBlog');
    super(props);
    const state = Plain.deserialize('Enter your blog here...');
    this.state = {
      state: state,
    }
  }
  
  onChange = (state) => {
    this.setState({state})
  }
  
  doPost = async () => {
    const state = this.state.state;
    const content = Plain.serialize(state);
    const res = await fetchJSON('POST', '/api/blog', {
      title: this.title.value,
      content: content,
    });
    if (res.ok) {
      console.log(res);
      this.props.history.push('/');
    } else {
      console.log(res);
    }
  }

  render() {
    return (
      <div className="center wide">
        <input ref={(input) => this.title = input}
          placeholder="Enter your title here..."
          style={{
            minWidth: '800px',
            marginBottom: '1em',
            lineHeight: '1.2',
            padding: '.6em',
          }}
        />
        <Editor className="editor"
          style={{
            minWidth: '800px',
            minHeight: '100px',
            padding: '.5em',
          }}
          state={this.state.state}
          onChange={this.onChange}
        />
        <button onClick={this.doPost}
          style={{float: 'right', marginTop: '1em'}}
        >Post</button>
      </div>
    );
  }
}

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
    if (!res.ok) {
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
    const resp = await fetchJSON('GET', '/api/logout', {
      username: this.props.user.username
    });
    if (resp.ok) {
      window.location.href = '/';
      //this.props.history.push('/');
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
      <div className="center narrow center-children">
        <button onClick={this.doLogout}>Logout</button>
      </div>
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
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh'
      }}>
        <Header user={this.state.user}/>
        <main>
          <Route exact path="/" render={
            () => <Blogs username="fans656" user={this.state.user}/>
          }/>
          <Route path="/about" component={About}/>
          <Route path="/login" component={Login}/>
          <Route exact path="/blog" component={Blogs}/>
          <Route exact path="/blog/:title" render={
            (props) => <Blogs title={props.match.params.title}/>
          }/>
          <Route path="/new-blog" component={NewBlog}/>
          <Route path="/profile/:username" render={
            (props) => <Profile user={this.state.user} {...props}/>
          }/>
        </main>
        <footer className="reverse-color"><Link to="/">fans656's site</Link></footer>
      </div>
    );
  }
}

const history = createBrowserHistory();

ReactDOM.render((
  <Router history={history}>
    <Route path="/" component={App}/>
  </Router>
), document.getElementById('root'));
