import os

from flask import *


route = '/'


def handle(**env):
    return send_from_directory(os.getcwd(), 'index.html')
