import logging
import os

import h5py
import numpy as np
from PIL import Image

from .models.db import engine
from .utils import IteratorFile
import settings

logger = logging.getLogger(__name__)

_distribution_file = None


def h5py_dataset_to_numpy(func):
    """ decorator to convert a first argument of h5py.Dataset to numpy.array """
    def decorator(*args, **kwargs):
        if type(args[0]) == h5py.Dataset:
            args = (args[0][:], ) + args[1:]
        return func(*args, **kwargs)
    return decorator


@h5py_dataset_to_numpy
def save_image(array, name):
    """saves 2d array of values 0-1 to a grayscale PNG"""
    array *= 255
    array = array.astype(np.uint8)
    image = Image.fromarray(array)
    png = os.path.join(settings.PNG_DIR, str(name) + '.png')
    logger.debug('writing {}'.format(png))
    image.save(png)


def create_output_file(force=False):

    new_file = True
    if os.path.isfile(settings.DISTRIBUTION_FILE):
        if force:
            os.unlink(settings.DISTRIBUTION_FILE)
        else:
            logger.info("Opening existing file {}".format(settings.DISTRIBUTION_FILE))
            new_file = False

    distribution_file = h5py.File(settings.DISTRIBUTION_FILE, 'a')

    if new_file:
        distribution_file.create_group('taxa')

        # dimensions = distribution_file.create_group('dimensions')
        distribution_file['latitude'] = np.arange(89.75, -90, -.5)
        distribution_file['longitude'] = np.arange(-179.75, 180, .5)

    return distribution_file


def get_distribution_file(force=False):

    global _distribution_file

    if not _distribution_file:
        _distribution_file = create_output_file(force=force)
    return _distribution_file


@h5py_dataset_to_numpy
def save_database(distribution, taxonkey):

    with engine.connect() as connection:
        # psycopg2 isn't using executemany, it is doing one insert
        # per record. Since the sqlalchemy connection object doesn't attempty to hide
        # the raw connection, use it to insert the data with psycopg2.copy_from

        raw_conn = connection.connection.connection
        cursor = raw_conn.cursor()
        cursor.execute("DELETE FROM taxon_distribution WHERE taxonkey = %s", (taxonkey, ))

        r = distribution.ravel()
        indexes = np.where(~np.isnan(r))[0]
        scaled_distribution = (r * 1000000000).astype(int)

        def records():
            for seq, value in zip(indexes + 1, scaled_distribution[indexes]):
                yield '{}\t{}\t{}\n'.format(taxonkey, seq, value)

        f = IteratorFile(records())
        cursor.copy_from(f, 'taxon_distribution', columns=('taxonkey', 'cellid', 'relativeabundance'))
        raw_conn.commit()


def save_hdf5(distribution, taxon, force=None):
    distribution[distribution.mask] = np.nan

    distribution_file = get_distribution_file(force=force)
    dataset = distribution_file.create_dataset('taxa/' + str(taxon.taxonkey), data=distribution)

    dataset.dims[0].attach_scale(distribution_file['latitude'])
    dataset.dims[1].attach_scale(distribution_file['longitude'])


def save(distribution, taxon, force=False):
    """ creates products for distribution and taxon """

    save_database(distribution, taxon.taxonkey)
    save_hdf5(distribution, taxon, force=force)
    save_image(array=distribution, name=taxon.taxonkey)


def close():

    global _distribution_file
    _distribution_file.close()


def completed_taxon():
    distribution_file = get_distribution_file()
    return distribution_file.keys()
