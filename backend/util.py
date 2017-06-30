# coding: utf-8
import os
import random
import functools
import traceback
from datetime import datetime, timedelta

import flask
from flask import redirect, jsonify
from dateutil.parser import parse as parse_datetime


def handle_exceptions(viewfunc):
    @functools.wraps(viewfunc)
    def wrapper(*args, **kwargs):
        try:
            return viewfunc(*args, **kwargs)
        except Exception as e:
            return error_response(e)
    return wrapper


def success_response(data=None):
    if data is None:
        data = {}
    elif isinstance(data, (str, unicode)):
        data = {'detail': data}
    data.update({'errno': 0})
    return jsonify(**data)

def error_response(detail, status_code=400):
    if isinstance(detail, dict):
        data = detail
        detail = detail.get('detail', '')
    elif isinstance(detail, Exception):
        detail = traceback.format_exc(detail)
        print detail
        data = {}
    else:
        data = {}
    data.update({
        'errno': status_code,
        'detail': detail,
    })
    resp = jsonify(**data)
    resp.status_code = status_code
    return resp


def send_from_directory(*paths):
    fpath = os.path.join(*paths)
    fpath = os.path.abspath(fpath)
    if not fpath.startswith(paths[0]):
        raise errors.NotAllowed('are you up to something?')
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    return flask.send_from_directory(dirname, fname)


def utcnow():
    return str(datetime.utcnow()) + ' UTC'


def id_from_ctime(ctime):
    dt = parse_datetime(ctime)
    if dt.minute == dt.second == dt.microsecond == 0:
        dt += timedelta(microseconds=random.randint(0, 999999))
    return dt.strftime('%Y%m%d%H%M%SUTC%f')
