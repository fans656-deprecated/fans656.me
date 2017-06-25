import os
import subprocess
from datetime import datetime

import config

pause = True

def execute(cmd, replacecmd=None):
    print
    print replacecmd or cmd
    if pause:
        raw_input('=' * 8 + ' about to execute, press enter to execute...')
    os.system(cmd)

if __name__ == '__main__':
    root = config.BACKUP_REPO_DIR

    if not os.path.exists(root):
        os.makedirs(root)

    repo_file_dir = os.path.abspath(root) + '/'
    local_file_dir = os.path.abspath('./files')
    dump_fpath = os.path.join(root, '{}.sql'.format(config.db_name))

    # rsync files
    execute('rsync -av {} {}'.format(local_file_dir, repo_file_dir))

    execute('mysqldump -u{user} -p{pwd} {db} > {fpath}'.format(
        user=config.db_username,
        db=config.db_name,
        pwd=config.db_password,
        fpath=dump_fpath,
    ), replacecmd='Going to mysqldump {} to {}'.format(
        config.db_name, dump_fpath,
    ))

    os.chdir(root)
    execute('pwd')
    if not os.path.exists('.git'):
        execute('git init')
    if not subprocess.check_output('git remote -v', shell=True):
        execute('git remote add origin {}'.format(config.DATA_REMOTE_REPO))

    execute('git add --all')
    execute('git commit -m "{}"'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    execute('git push origin master')

    print 'backed up at {}'.format(datetime.now())
