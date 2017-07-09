import React, { Component } from 'react'

import { fetchData } from './utils'

export default class Gallery extends Component {
  constructor(props) {
    super(props);
    const files = this.props.json.files;
    this.cols = this.props.json.cols || 4;
    this.files = [];
    this.paths = [];
    this.descriptions = [];
    for (let path of files) {
      let fpath = path;
      let description = '';
      if (typeof(path) !== 'string') {
        fpath = path.path;
        description = path.description;
      }
      this.descriptions.push(description);
      const parts = fpath.split('/');
      const fname = parts[parts.length - 1];
      if (description.length === 0) {
        description = fname;
      }
      if (fname.match(/.*\..*/)) {
        this.files.push(fpath);
      } else {
        this.paths.push(fpath);
      }
    }
    this.state = {
      srcs: [],
      description: [],
    };
  }

  componentDidMount() {
    fetchData('POST', '/api/get-gallery', {
      files: this.files,
      paths: this.paths,
    }, res => {
      this.setState({
        srcs: res.srcs,
      });
    });
  }

  render() {
    console.log(this.descriptions);
    const srcs = this.state.srcs;
    if (this.props.viewtype === 'item') {
      return <div>
        <a className="gallery item-view" href={this.props.blogURL}
          onClick={(ev) => {
            ev.preventDefault();
            window.open(this.props.blogURL, '_blank');
        }}>
          {srcs.slice(0, 8).map(src => <img src={src + '?width=200'} style={{
            maxWidth: '20%',
          }}/>)}
        </a>
        <p className="info filter" style={{textAlign: 'center'}}
        >{srcs.length + ' pics'}</p>
      </div>
    } else {
      const isMobile = window.matchMedia(
        '(max-device-width: 800px)').matches;
      const windowWidth = window.innerWidth;
      return <div className="gallery">
        {
          srcs.map((src, i) => {
            const parts = src.split('/');
            const fname = parts[parts.length - 1];
            const name = fname.match(/(.*)\.[^.]*/)[1];
            let width = isMobile
              ? windowWidth : Math.floor(window.innerWidth / this.cols);
            width = Math.max(400, width);
            const description = this.descriptions[i] || name;
            return <div className="img"
              key={i}
              style={{
                maxWidth: isMobile ? '100%' : `${90 / this.cols}%`,
              }}
            >
              <img
                src={src + `?width=${width}`}
                title={description}
                onClick={() => {window.open(src, '_blank');}}
                style={{
                  width: '100%',
                }}
              />
              {this.props.json['show-description'] &&
                  <p style={{
                    textAlign: 'center',
                    fontSize: '.8rem',
                  }}>{description}</p>
              }
            </div>
          })
        }
      </div>
    }
  }
}
