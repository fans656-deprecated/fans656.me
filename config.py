session_duration_days = 7
sweep_expires_probability = 1.0 / 1000

#db_engine = 'sqlite'
db_engine = 'mysql'

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

local = True
import os
if os.path.exists('nginx.conf'):
    local = False

server_name = 'fans656.me'
if local:
    server_name = 'local.dev'
