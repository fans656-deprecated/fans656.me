#!/usr/bin/env python
import sys
from getpass import getpass

from utils.user import create_user

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Creating user "fans656"'
        create_user('fans656', getpass())
    else:
        print 'todo'
