import React, { Component } from 'react'

export default class Files extends Component {
  render() {
    return <div className="center-children" style={{margin: '3em'}}>
      <button id="upload" onClick={() => this.fileInput.click()}>
        Upload
      </button>
      <input
        type="file"
        multiple
        style={{display: 'none'}}
        onChange={this.onUploadFileChange}
        ref={ref => this.fileInput = ref}
      />
    </div>
  }

  onUploadFileChange = ({target}) => {
    console.log(target.files);
    const file = target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = ({target}) => {
        const content = target.result;
        console.log(content.substring(0, 80));
      }
      reader.readAsBinaryString(file);
    }
  }
}

export class FileExplorer extends Component {
  render() {
    return <div style={{
      height: 400,
      border: '1px solid #aaa',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    }}>
      <h1>this is the file explorer</h1>
    </div>
  }
}
