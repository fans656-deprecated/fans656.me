import os

from flask import request

import config
from config import CHUNK_SIZE
from errors import Existed, ServerError, BadRequest

INVALID_CHARS = set(r'\*?"[]{}<>:;|=,~`!@#$%^&' + "'")

def save(fpath, total_size):
    user_fpath = fpath
    fpath = os.path.join(config.FILES_ROOT, fpath)
    if os.path.exists(fpath) and os.path.isdir(fpath):
        raise Existed('path {} will overwrite a directory'.format(user_fpath))
    if any(ch in INVALID_CHARS for ch in fpath):
        raise BadRequest('invalid path {}'.format(user_fpath))
    # create directory
    user_dirpath = os.path.dirname(fpath)
    dirpath = os.path.abspath(user_dirpath)
    if not dirpath.startswith(config.FILES_ROOT):
        raise NotAllowed(
            'are you trying to do something? {}'.format(user_fpath))
    if not os.path.exists(dirpath):
        try:
            os.makedirs(dirpath)
        except Exception as e:
            raise ServerError('make directory {} failed: {}'.format(
                user_dirpath, e.message,
            ))
    assert os.path.exists(dirpath)
    if not os.path.isdir(dirpath):
        raise Existed(
            'requested directory {} is not available'.format(user_dirpath))
    # do save
    try:
        with open(fpath, 'wb') as f:
            received_size = 0
            while received_size < total_size:
                chunk = request.stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                received_size += len(chunk)
                if received_size > total_size:
                    extra_size = received_size - total_size
                    chunk = chunk[:-extra_size]
                f.write(chunk)
    except Exception as e:
        raise ServerError(e.message)

def rooted_path(root, path):
    root = os.path.abspath(root)
    path = os.path.abspath(os.path.join(root, path))
    if not path.startswith(root):
        return None
    return path

def list_file_directory(dirpath):
    user_dirpath = dirpath
    rootpath = rooted_path(config.FILES_ROOT, '')
    dirpath = rooted_path(rootpath, dirpath)
    if not dirpath:
        return []
    host = get_host_from_url(request.url)
    endpoint_dirpath = os.path.join('file', dirpath)
    res = []
    if dirpath != rootpath:
        name = os.path.basename(os.path.basename(dirpath))
        path = os.path.dirname(dirpath)[len(rootpath):]
        if path and path[0] == '/':
            path = path[1:]
        res.append({
            'name': '..',
            'path': path,
            'url': '',
            'isdir': True,
        })
    for fname in os.listdir(dirpath):
        fpath = os.path.join(dirpath, fname)
        user_fpath = os.path.join(user_dirpath, fname)
        isdir = os.path.isdir(fpath)
        if isdir:
            url = 'api/file/' + user_fpath
        else:
            url = 'file/' + user_fpath
        url = host + '/' + url
        res.append({
            'name': fname,
            'path': user_fpath,
            'url': url,
            'isdir': isdir,
        })
    return res

def get_host_from_url(url):
    cnt = 0
    for i, c in enumerate(url):
        if c == '/':
            cnt += 1
        if cnt == 3:
            return url[:i]
    return None