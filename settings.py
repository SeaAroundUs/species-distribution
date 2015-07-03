# settings for species-distribution

DEBUG = True

NUMPY_WARNINGS = 'warn'  # ‘ignore’, ‘warn’, ‘raise’, ‘call’, ‘print’, ‘log’}
# NUMPY_WARNINGS = 'call'  # ‘ignore’, ‘warn’, ‘raise’, ‘call’, ‘print’, ‘log’}

DISTRIBUTION_FILE = 'species-distribution.hdf5'
PNG_DIR = 'png'

DB = {
    'username': 'web',
    'password': 'web',
    'host': 'localhost',
    'port': '5432',
    'db': 'specdis',
}

try:
    from local_settings import *
except ImportError:
    print('define local_settings.py to override settings')
