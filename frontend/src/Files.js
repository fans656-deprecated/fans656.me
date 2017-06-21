import React, { Component } from 'react'

import { fetchJSON } from './utils'
import { BACKEND_HOST } from './conf'

export default class Files extends Component {
  constructor(props) {
    super(props);
    this.state = {
      files: [],
      dirpath: '',
    };
  }

  render() {
    return <div id="files-page" className="center-children">
      <FileExplorer/>
      <button className="primary"
        onClick={() => this.fileInput.click()}
      >
        Upload
      </button>
      <input type="text"
        value={this.state.dirpath}
        onChange={({target}) => this.setState({dirpath: target.value})}
        placeholder="Directory path"
        style={{marginTop: '2em', minWidth: '30em', padding: '0 .3em'}}
      />
      <input
        type="file"
        multiple
        style={{display: 'none'}}
        onChange={this.onUploadFileChange}
        ref={ref => this.fileInput = ref}
      />
    </div>
  }

  doUpload = () => {
    const files = this.state.files;
    console.log('doUpload');
    console.log(files);
    for (const file of files) {
      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (ev) => {
        console.log('upload progress');
        console.log(ev);
      };
      xhr.onload = ({target}) => {
        const res = JSON.parse(target.response);
        if (res.errno) {
          console.log('upload error');
        } else {
          console.log('upload ok');
        }
        console.log(res);
      };
      let dirpath = this.state.dirpath;
      if (dirpath[dirpath.length - 1] !== '/') {
        dirpath = dirpath + '/';
      }
      let fpath = dirpath + file.name;
      // TODO: validate path
      if (fpath[0] === '/') {
        fpath = fpath.substring(1, fpath.length);
      }
      const url = BACKEND_HOST + '/api/file/' + fpath;
      console.log('uploading to ' + url);
      xhr.open('POST', url, true);
      xhr.withCredentials = true;
      xhr.send(file);
    }
    this.fileInput.value = null;
  }

  onUploadFileChange = ({target}) => {
    console.log('onUploadFileChange');
    this.setState({files: target.files}, this.doUpload);
  }
}

export class FileExplorer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      path: '',
      files: [],
    };
  }

  render() {
    const fileItems = this.state.files.map((file) => {
      const name = file.name + (file.isdir ? '/' : '');
      let liChild;
      if (file.isdir) {
        liChild = <span>{name}</span>;
      } else {
        liChild = (
          <a
            href={file.url}
            style={{display: 'block', width: '100%'}}
            onClick={(ev) => ev.preventDefault()}
          >
            {name}
          </a>
        );
      }
      return <li
        className={file.isdir ? 'dir' : ''}
        key={file.url}
        onClick={() => {
          if (file.isdir) {
            this.setState({path: file.path}, this.fetchFileList);
          } else {
            window.open(file.url, '_blank');
          }
        }}
      >
        {liChild}
      </li>
    });
    return (
      <div className="file-explorer">
        <p style={{fontSize: '.8em', borderBottom: '1px solid #ddd'}}>{'/' + this.state.path}</p>
        <ul className="file-list">
          {fileItems}
        </ul>
      </div>
    )
  }

  componentDidMount() {
    this.fetchFileList();
  }

  fetchFileList = async () => {
    const path = this.state.path;
    const url = '/api/file' + (path ? '/' + path : '');
    const res = await fetchJSON('GET', url + '?' + new Date().getTime());
    if (res.errno) {
      console.log(res);
    } else {
      this.setState({files: res.files});
    }
  }
}
