session_duration_days = 7
sweep_expires_probability = 1.0 / 1000

#db_engine = 'sqlite'
db_engine = 'mysql'

try:
    from secret_config import *
except ImportError:
    pass
