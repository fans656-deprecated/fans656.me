#!/usr/bin/env python
import sys

from user_util import delete_user

if len(sys.argv) > 1:
    username = sys.argv[1]
    print 'deleting user "{}"'.format(username)
    print delete_user(username)
