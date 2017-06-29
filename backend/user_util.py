import os, hashlib, binascii

import db
from util import utcnow


def try_auth(username, password):
    assert exists(username), 'user does not exist'
    salt, expected_hashed_password = db.query_one(
        'match (u:User{username: {username}}) '
        'return u.salt, u.hashed_password', {
            'username': username
        }
    )
    _, got_hashed_password = get_hashed_salt_and_password(password, salt)
    print 'hashes (got/expected)'
    print got_hashed_password
    print expected_hashed_password
    assert got_hashed_password == expected_hashed_password, 'invalid auth'


def create_user(username, password):
    salt, hashed_password = get_hashed_salt_and_password(password)
    return db.execute('''
        create (n:User{
            username: {username},
            salt: {salt},
            hashed_password: {hashed_password},
            created_at: {created_at}
        })
               '''
        , {
            'username': username,
            'salt': salt,
            'hashed_password': hashed_password,
            'created_at': utcnow(),
        }
    )


def delete_user(username):
    return db.execute(
        'match (n:User{username: {username}}) detach delete n'
        , {
            'username': username,
        }
    )


def exists(username):
    return db.query_one(
        'match (n:User{username: {username}}) return count(n)'
        , {'username': username}
    ) != 0


def get_hashed_salt_and_password(password, salt=None):
    if salt is None:
        salt = binascii.hexlify(os.urandom(32))
    hashed_pwd = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    hashed_pwd = binascii.hexlify(hashed_pwd)
    return salt, hashed_pwd
