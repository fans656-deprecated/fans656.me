import os

import flask
from flask import current_app as app
import requests

import config

def leetcode():
    try:
        text = requests.get(config.leetcode_url).text
    except Exception:
        text = 'Get {} failed, go to debug?'.format(url)
    return flask.render_template_string('''
<head>
    <link rel="stylesheet" href="{{css}}"/>
</head>
<body>
    {{text|markdown}}
</body>
            ''', text=text, css=config.leetcode_css_url)
