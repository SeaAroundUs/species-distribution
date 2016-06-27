import subprocess

from setuptools import setup, find_packages

def get_hash():
    return subprocess \
            .check_output(('git', 'rev-parse', '--short', 'HEAD')) \
            .strip() \
            .decode('ascii')

# NOTE:
# For ubuntu, there are os-level packages that also need to be installed. These are the minimum found to be necessary
# to support the list of python packages specified below:
#       sudo apt-get install libpng-dev libjpeg8-dev libfreetype6-dev pkg-config python-matplotlib python3-matplotlib
#

setup(
    name='species_distribution',
    version='2.0.1',
    description='Species distribution for Sea Around Us Project',
    test_suite='unittest2.collector',
    packages=find_packages(),
    install_requires=['Cython', 'six', 'unittest2', 'numpy', 'psycopg2', 'python-dateutil', 'SQLAlchemy', 'pyproj', 'matplotlib', 'pillow'],
    scripts=[
        'bin/h5-to-database',
        'bin/h5-to-png',
        'bin/species-distribution'
    ],
)
