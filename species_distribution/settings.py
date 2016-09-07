# settings for species-distribution

import json
import os
import sys

user_settings_dir = os.getcwd()
user_settings_file = os.path.join(user_settings_dir, '.settings.json')

settings = {

    'DEBUG': False,
    'NUMPY_WARNINGS': 'warn',
    'PNG_DIR': 'png',

    'DB': {
        'username': 'web',
        'password': 'web',
        'host': 'localhost',
        'port': '5432',
        'db': 'specdis'
    },

    'USER_SETTINGS_DIR': user_settings_dir,
    'USER_SETTINGS_FILE': user_settings_file
}

locals().update(settings)

# override with user settings in ./species-distribution/.settings.json
try:

    if not os.path.isdir(user_settings_dir):
        os.makedirs(user_settings_dir)

    if not os.path.isfile(user_settings_file):
        with open(user_settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    user_settings = json.load(open(user_settings_file))
    locals().update(user_settings)
except:
    raise Exception('unable to open user settings {}'.format(user_settings_file))

