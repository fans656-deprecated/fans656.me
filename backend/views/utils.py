from flask import jsonify

def ok(data={}):
    res = {'status': 'ok'}
    res.update(data)
    return jsonify(**res)

def error(detail):
    return jsonify(**{
        'status': 'error',
        'detail': detail,
    })

