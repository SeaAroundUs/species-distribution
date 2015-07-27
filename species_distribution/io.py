import functools
import logging
import os

import numpy as np

from .models.db import engine, Session

from .utils import IteratorFile
import settings

logger = logging.getLogger(__name__)


def save_image(array, name, enhance=False):
    """saves 2d array of values 0-1 to a grayscale PNG"""

    import matplotlib.pyplot as plt
    from PIL import Image, ImageOps

    if not os.path.isdir(settings.PNG_DIR):
        os.makedirs(settings.PNG_DIR)

    png = os.path.join(settings.PNG_DIR, str(name) + '.png')
    logger.debug('writing {}'.format(png))

    array = plt.cm.jet(array) * 255
    array = array.astype(np.uint8)
    image = Image.fromarray(array)
    if enhance:
        image = ImageOps.equalize(image)
        image = ImageOps.autocontrast(image)
    image.save(png)


def save_database(distribution, taxonkey):

    with engine.connect() as connection:
        # psycopg2 isn't using executemany, it is doing one insert
        # per record. Since the sqlalchemy connection object doesn't attempty to hide
        # the raw connection, use it to insert the data with psycopg2.copy_from

        raw_conn = connection.connection.connection
        cursor = raw_conn.cursor()
        cursor.execute("DELETE FROM taxon_distribution WHERE taxon_key = %s", (taxonkey, ))

        ravel = distribution.ravel()
        indexes = np.where(~(np.isnan(ravel) | ravel.mask))[0]

        def records():
            for seq, value in zip(indexes + 1, ravel[indexes]):
                yield '{}\t{}\t{}\n'.format(taxonkey, seq, value)

        f = IteratorFile(records())
        cursor.copy_from(f, 'taxon_distribution', columns=('taxon_key', 'cell_id', 'relative_abundance'))
        raw_conn.commit()


@functools.lru_cache()
def completed_taxon():
    """returns a sequence of taxon_keys already present"""
    with Session() as session:
        query = """
        SELECT DISTINCT taxon_key from taxon_distribution
        """
        result = session.execute(query)
        return [x[0] for x in result]
