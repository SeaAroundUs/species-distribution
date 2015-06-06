import logging
import os

import h5py
import numpy as np
from PIL import Image

from .models.db import engine
import settings

logger = logging.getLogger(__name__)

_distribution_file = None


def save_image(array, name):
    """saves 2d array of values 0-1 to a grayscale PNG"""
    array *= 255
    array = array.astype(np.uint8)
    image = Image.fromarray(array)
    png = os.path.join(settings.PNG_DIR, str(name) + '.png')
    logger.debug('writing {}'.format(png))
    image.save(png)


def insert_distribution_table(distribution, taxon):
    with engine.connect() as connection:

        connection.execute("DELETE FROM taxon_distribution WHERE taxonkey = %s", taxon.taxonkey)

        query = "INSERT INTO taxon_distribution (taxonkey, cellid, relativeabundance) VALUES (%s, %s, %s)"

        def records():
            for x in range(distribution.shape[1]):
                for y in range(distribution.shape[0]):
                    if not distribution.mask[y, x]:
                        seq = (x + y * distribution.shape[1]) + 1
                        yield taxon.taxonkey, seq, distribution[y, x]

        connection.execute(query, list(records()))


def create_output_file(force=False):

    if os.path.isfile(settings.DISTRIBUTION_FILE):
        if force:
            os.unlink(settings.DISTRIBUTION_FILE)
        else:
            logger.warn("Appending to existing file {}".format(settings.DISTRIBUTION_FILE))

    return h5py.File(settings.DISTRIBUTION_FILE, 'a')


def get_distribution_file(force=False):

    global _distribution_file

    if not _distribution_file:
        _distribution_file = create_output_file(force=force)
    return _distribution_file


def save(distribution, taxon, force=False):
    """ creates products for distribution and taxon """

    insert_distribution_table(distribution, taxon)

    save_image(array=distribution, name=taxon.taxonkey)

    distribution_file = get_distribution_file(force=force)
    distribution_file.create_dataset(str(taxon.taxonkey), data=distribution)


def close():

    global _distribution_file
    _distribution_file.close()

def completed_taxon():
    distribution_file = get_distribution_file()
    return distribution_file.keys()
