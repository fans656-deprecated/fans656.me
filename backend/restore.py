#!/usr/bin/env python
import os
import subprocess
from datetime import datetime

import conf

pause = False

def execute(cmd, replacecmd=None):
    print
    print replacecmd or cmd
    if pause:
        raw_input('=' * 8 + ' about to execute, press enter to execute...')
    os.system(cmd)

if __name__ == '__main__':
    # e.g. "/home/fans656/data-fans656.me"
    backup_repo_dir = conf.BACKUP_REPO_DIR
    backup_file_dir = os.path.join(backup_repo_dir, 'files')
    local_file_dir = conf.FILES_ROOT
    dump_fpath = os.path.join(backup_repo_dir,
                              '{}.sql'.format(conf.db_name))

    execute('rsync -av {}/ {}'.format(backup_file_dir, local_file_dir))

    execute('mysql -u{user} -p{pwd} -D{db} < {fpath}'.format(
        user=conf.db_username,
        db=conf.db_name,
        pwd=conf.db_password,
        fpath=dump_fpath,
    ), replacecmd='mysql -D{} < {}'.format(
        conf.db_name, dump_fpath,
    ))

    print
    print
    print '*' * 70
    print 'OK! Data restored at {}'.format(datetime.now())
