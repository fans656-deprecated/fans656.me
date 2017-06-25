import os

abspath = os.path.abspath

THIS_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

FILES_ROOT = abspath(os.path.join(THIS_SCRIPT_DIR, '../files/'))
BACKUP_REPO_DIR = os.path.expanduser('~/data-fans656.me/')
FRONTEND_BUILD_DIR = abspath(os.path.join(THIS_SCRIPT_DIR, '../frontend/build'))

PORT = 6560

print 'Configurations:'
indent = ' ' * 4
for k, v in globals().items():
    if k.isupper():
        print indent + '{} = {}'.format(k, v)

FILE_RECEIVE_CHUNK_SIZE = 4096

session_duration_days = 7
sweep_expires_probability = 1.0 / 1000

#db_engine = 'sqlite'
db_engine = 'mysql'

encoding = 'utf8'

try:
    from secret_config import *
except ImportError:
    import os
    print 'Please decrypt the secret_config.py.gpg file'
    os.system('gpg -o secret_config.py secret_config.py.gpg')
    try:
        from secret_config import *
    except ImportError:
        print 'Failed to import secret_config'

BACKUP_DUMP_FNAME = '{}.sql'.format(db_name)

local = True
import os
if os.path.exists('nginx.conf'):
    local = False

server_name = 'fans656.me'
if local:
    server_name = 'local.dev'
