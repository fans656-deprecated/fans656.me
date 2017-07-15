import React, { Component } from 'react'
import ECharts from 'react-echarts'
import _ from 'lodash'

import { fetchData } from './utils'

export default class Gallery extends Component {
  constructor(props) {
    super(props);
    this.state = {
      dates: [],
      counts: [],
      blogLinks: [],
      total: 0,
    };
  }

  componentDidMount() {
    fetchData('GET', '/api/leetcode-statistics', res => {
      this.setState({
        dates: res.dates.map(strDate => {
          const date = new Date(strDate);
          return (date.getMonth() + 1) + '-' + date.getDate();
        }),
        counts: res.counts,
        blogLinks: res.blog_links,
        total: res.total,
      });
    });
  }

  render() {
    return <div style={{marginBottom: '2em'}}>
      <ECharts option={{
        xAxis: {
          data: this.state.dates,
        },
        yAxis: {},
        tooltip: {},
        series: [{
          type: 'bar',
          itemStyle: {
            normal: {
              color: 'steelblue',
            },
          },
          data: this.state.counts,
        }]
      }} style={{
        width: '100%',
        height: 400,
      }}/>
      <div style={{textAlign: 'right'}}>
        <h3>{this.state.total}</h3>
      </div>
      {this.props.isSingleView &&
        <ul style={{
          listStyle: 'none',
          margin: 0,
          padding: 0,
        }}>
          {this.state.blogLinks.reverse().map(blogs => (
            <div style={{
              marginBottom: '1em',
            }}>
              {blogs.map(link => (
                <li>
                  <a
                    href={link.url}
                    title={link.title}
                  >
                    <span>{link.title}</span>
                    <span className="info filter" style={{
                      float: 'right',
                      fontSize: '.7em',
                    }}>
                      {new Date(link.date).toLocaleString()}
                    </span>
                  </a>
                </li>
              ))}
            </div>
          ))}
        </ul>
      }
    </div>
  }
}
