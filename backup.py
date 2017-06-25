import os

import config

root = config.BACKUP_REPO_DIR

if not os.path.exists(root):
    os.makedirs(root)

repo_file_dir = os.path.abspath(root) + '/'
local_file_dir = os.path.abspath('./files')
dump_fpath = os.path.join(root, '{}.sql'.format(config.db_name))

print 'rsync {} to {}'.format(local_file_dir, repo_file_dir)
raw_input()
os.system('rsync -a {} {}'.format(local_file_dir, repo_file_dir))

print 'mysqldump {}'.format(config.db_name)
raw_input()
os.system('mysqldump -u{user} -p{pwd} {db} > {fpath}'.format(
    user=config.db_username,
    db=config.db_name,
    pwd=config.db_password,
    fpath=dump_fpath,
))

os.chdir(root)
if not os.path.exists('.git'):
    print 'git init at {}'.format(os.path.abspath('.'))
    raw_input()
    os.system('git init')
    os.system('git remote origin add {}'.format(config.DATA_REMOTE_REPO))

print 'git add & commit & push to {}'.format(config.DATA_REMOTE_REPO)
raw_input()
os.system('git add --all')
os.system('git commit -m "{}"'.format(
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))
os.system('git push origin master')

print 'backed up at {}'.format(datetime.now())
