import subprocess

from setuptools import setup, find_packages

def get_hash():
    return subprocess \
            .check_output(('git', 'rev-parse', '--short', 'HEAD')) \
            .strip() \
            .decode('ascii')

setup(
    name='species_distribution',
    version='2.0.1',
    description='Species distribution for Sea Around Us Project',
    test_suite='unittest2.collector',
    packages=find_packages(),
    install_requires=['Cython', 'six', 'unittest2', 'numpy', 'psycopg2', 'python-dateutil', 'SQLAlchemy', 'pyproj'],
    scripts=[
        'bin/h5-to-database',
        'bin/h5-to-png',
        'bin/species-distribution'
    ],
)
