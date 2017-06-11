import os, hashlib, binascii

import db

class UserExisted(Exception): pass

class InvalidAuth(Exception):

    def __init__(self, msg='username or password incorrect'):
        super(InvalidAuth, self).__init__(msg)

def exists(username):
    return bool(db.queryone('select count(*) from users where username = %s',
                         (username,)))

def hash_pass(password, salt=None, iterations=100000):
    if salt is None:
        salt = binascii.hexlify(os.urandom(32))
    hashed_pwd = hashlib.pbkdf2_hmac('sha256', password, salt, iterations)
    hashed_pwd = binascii.hexlify(hashed_pwd)
    return salt, hashed_pwd, iterations

def register(username, password):
    if exists(username):
        raise UserExisted('username is taken by someone else')
    db.execute('insert into users (username, salt, hashed_pwd, iterations) values'
              '(%s, %s, %s, %s)', (username,) + hash_pass(password))
    print 'register user "{}" successfully'.format(username)

def login(username, password):
    if not exists(username):
        raise InvalidAuth()
    salt, expected_hashed_pwd, iterations = db.queryone(
        'select salt, hashed_pwd, iterations from users where username = %s',
        (username,))
    _, hashed_pwd, _ = hash_pass(password, salt=salt, iterations=iterations)
    if hashed_pwd != expected_hashed_pwd:
        raise InvalidAuth()

def valid_auth(username, password):
    try:
        login(username, password)
        return True
    except InvalidAuth:
        return False

if __name__ == '__main__':
    register('a', 'b')
