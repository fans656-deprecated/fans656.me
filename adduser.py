import os
import hashlib

def salted(pwd):
    salt = os.urandom(16)
    salted_pwd = hashlib.pbkdf2_hmac('sha1', pwd, salt, 100000)
    return salt, salted_pwd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
