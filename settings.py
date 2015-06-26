# settings for species-distribution

DEBUG = True

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
