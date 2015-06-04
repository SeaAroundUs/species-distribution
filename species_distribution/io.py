import logging
import os

import h5py
import numpy as np
from PIL import Image

import settings

logger = logging.getLogger(__name__)


def save_image(array, name):
    """saves 2d array of values 0-1 to a grayscale PNG"""
    array *= 255
    array = array.astype(np.uint8)
    image = Image.fromarray(array)
    png = os.path.join(settings.PNG_DIR, str(name) + '.png')
    logger.debug('writing {}'.format(png))
    image.save(png)


def create_output_file(force=False):

    if os.path.isfile(settings.DISTRIBUTION_FILE):
        if force:
            os.unlink(settings.DISTRIBUTION_FILE)
        else:
            logger.warn("Appending to existing file {}".format(settings.DISTRIBUTION_FILE))

    return h5py.File(settings.DISTRIBUTION_FILE, 'a')

