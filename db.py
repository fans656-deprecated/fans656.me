import os
import imp
import sys
import json
import tempfile
import sqlite3
import hashlib
import traceback
import importlib

import requests
from flask import g

import conf


def getdb():
    if not hasattr(g, '_db'):
        g._db = sqlite3.connect(conf.dbname)
    return g._db


def get_route():
    c = getdb().cursor()
    c.execute('select * from route')
    return [
        {'route': route, 'type': type, 'data': data}
        for route, type, data in c.fetchall()
    ]


def create_route_from_script_content(route, script_content):
    db = getdb()
    db.execute(
        'insert or replace into route (route, type, data) values (?, ?, ?)',
        (route, 'script', script_content)
    )
    db.commit()


def create_route_from_package(route, data):
    db = getdb()
    db.execute(
        'insert or replace into route (route, type, data) values (?, ?, ?)',
        (route, 'package', data)
    )
    db.commit()


def get_handler_module(path):
    handler_module = sys.modules.get(path)
    if handler_module:
        return handler_module
    c = getdb().cursor()
    c.execute('select type, data from route where route = ?', (path,))
    r = c.fetchone()
    if not r:
        return None
    type, data = r
    if type == 'script':
        try:
            fd, fpath = tempfile.mkstemp()
            with os.fdopen(fd, 'w') as f:
                f.write(data)
            handler_module = imp.load_source(path, fpath)
            print 'get_handler_module', dir(handler_module)
            return handler_module
        finally:
            os.remove(fpath)
            os.remove(fpath + 'c')
    elif type == 'package':
        name = json.loads(data)['name']
        module = importlib.import_module('handler.' + name)
        print module
        #sys.modules[path] = module
        module.working_dir = 'handler/{}/'.format(name)
        return module
    else:
        return None


def init_db():
    db = sqlite3.connect(conf.dbname)
    db.execute('drop table if exists route')
    db.execute('''
        create table route (
            route text primary key,
            type text,
            data text
        )
               ''')
    for path, dirs, fnames in os.walk('handler'):
        if 'handler.py' in fnames:
            try:
                handler = imp.load_source('tmp', os.path.join(path, 'handler.py'))
                route = handler.route
                module_name = os.path.basename(path)
                db.execute('insert or replace into route values (?, ?, ?)',
                           (route, 'package', json.dumps({
                               'name': module_name
                           })))
                print route, module_name
            except Exception as e:
                traceback.print_exc(e)
    db.commit()


def get_script_fpath(fname):
    if not os.path.exists(conf.script_dir):
        os.makedirs(conf.script_dir)
    return os.path.join(conf.script_dir, fname)


if __name__ == '__main__':
    init_db()
