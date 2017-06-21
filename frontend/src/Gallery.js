import React, { Component } from 'react'

import { fetchJSON } from './utils'

export default class Gallery extends Component {
  constructor(props) {
    super(props);
    this.state = {
      files: [],
    };
  }

  componentDidMount() {
    this.fetchImages();
  }

  fetchImages = async () => {
    const res = await fetchJSON('GET', '/api/file/images/girls/nude');
    if (!res.errno) {
      this.setState({files: res.files});
    }
  }

  render() {
    const images = this.state.files.filter((file) => file.url).map((file) => {
      return <div className="image-container" key={file.url}>
        <img src={file.url} alt={file.name}
          onClick={() => window.open(file.url, '_blank')}
        />
      </div>
    });
    return <div className="gallery">
      {images}
    </div>
  }
}
