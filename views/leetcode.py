import os

import flask
from flask import current_app as app
import requests

import config

def leetcode():
    try:
        text = requests.get(config.leetcode_url).text
        css = requests.get(config.leetcode_css_url).text
    except Exception:
        text = 'Get {} failed, go to debug?'.format(url)
        css = ''
    s = flask.render_template_string('''
<head>
<style>
{}
</style>
</head>
<body>
    {{{{text|markdown}}}}
</body>
            '''.format(css), text=text)
    print s
    return s
