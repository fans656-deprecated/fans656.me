#!/usr/bin/env/ python
import os
import subprocess
from datetime import datetime

import conf

pause = True

def execute(cmd, replacecmd=None):
    print
    print replacecmd or cmd
    if pause:
        raw_input('=' * 8 + ' about to execute, press enter to execute...')
    if os.system(cmd):
        print 'ERROR! backup failed'
        exit(1)

if __name__ == '__main__':
    root = conf.BACKUP_REPO_DIR

    if not os.path.exists(root):
        os.makedirs(root)

    backup_repo_dir = conf.BACKUP_REPO_DIR
    backup_file_dir = os.path.join(backup_repo_dir, 'files')
    local_file_dir = conf.FILES_ROOT
    dump_fpath = os.path.join(backup_repo_dir, conf.BACKUP_DUMP_FNAME)

    # rsync files
    execute('rsync -av {} {}'.format(local_file_dir + '/',
                                     backup_file_dir + '/'))

    execute('mysqldump -u{user} -p{pwd} {db} > {fpath}'.format(
        user=conf.db_username,
        db=conf.db_name,
        pwd=conf.db_password,
        fpath=dump_fpath,
    ), replacecmd='Going to mysqldump {} to {}'.format(
        conf.db_name, dump_fpath,
    ))

    os.chdir(root)
    execute('pwd')
    if not os.path.exists('.git'):
        execute('git init')
    if not subprocess.check_output('git remote -v', shell=True):
        execute('git remote add origin {}'.format(conf.DATA_REMOTE_REPO))

    execute('git add --all')
    execute('git commit -m "{}"'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    execute('git push origin master')

    print 'backed up at {}'.format(datetime.now())
