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
    root = config.BACKUP_REPO_DIR

    repo_file_dir = os.path.abspath(root) + '/'
    local_file_dir = os.path.abspath('./files/')
    dump_fpath = os.path.join(root, '{}.sql'.format(config.db_name))

    execute('rsync -av {} {}'.format(
        os.path.join(repo_file_dir, 'files'),
        local_file_dir,
    ))

    #raw_input('About to restore mysql database, are you sure?')
    execute('mysql -u{user} -p{pwd} -D{db} < {fpath}'.format(
        user=config.db_username,
        db=config.db_name,
        pwd=config.db_password,
        fpath=dump_fpath,
    ), replacecmd='mysql -D{} < {}'.format(
        config.db_name, dump_fpath,
    ))

    print
    print 'data restored at {}'.format(datetime.now())
