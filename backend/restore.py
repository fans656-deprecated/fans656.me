#!/usr/bin/env python
import os
import subprocess
from datetime import datetime

import config

pause = False

def execute(cmd, replacecmd=None):
    print
    print replacecmd or cmd
    if pause:
        raw_input('=' * 8 + ' about to execute, press enter to execute...')
    os.system(cmd)

if __name__ == '__main__':
    # e.g. "/home/fans656/data-fans656.me"
    backup_repo_dir = config.BACKUP_REPO_DIR
    backup_file_dir = os.path.join(backup_repo_dir, 'files')
    local_file_dir = config.FILES_ROOT
    dump_fpath = os.path.join(backup_repo_dir,
                              '{}.sql'.format(config.db_name))

    execute('rsync -av {}/ {}'.format(backup_file_dir, local_file_dir))

    execute('mysql -u{user} -p{pwd} -D{db} < {fpath}'.format(
        user=config.db_username,
        db=config.db_name,
        pwd=config.db_password,
        fpath=dump_fpath,
    ), replacecmd='mysql -D{} < {}'.format(
        config.db_name, dump_fpath,
    ))

    print
    print
    print '*' * 70
    print 'OK! Data restored at {}'.format(datetime.now())
