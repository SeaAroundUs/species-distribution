from datetime import datetime
import functools
import logging
import os

import numpy as np

from .models.db import Session

from .utils import IteratorFile
from . import settings

logger = logging.getLogger(__name__)


def save_image(array, name, enhance=False):
    """saves 2d array of values 0-1 to a grayscale PNG"""

    if (array is None) or array.count() == 0:
        return

    import matplotlib
    matplotlib.use('Agg')
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

    with Session() as session:
        # psycopg2 isn't using executemany, it does one insert
        # per record. Use the sqlalchemy connection object to
        # insert the data with psycopg2.copy_from

        raw_conn = session.connection().connection
        cursor = raw_conn.cursor()
        cursor.execute("DELETE FROM taxon_distribution WHERE taxon_key = %s", (taxonkey, ))

        ravel = distribution.ravel()
        # don't include values which are NaN, masked, or smaller than machine epsilon
        # (approximately 0 valued)
        indexes = np.where(~(np.isnan(ravel) | ravel.mask | (ravel <= np.finfo(float).eps).mask))[0]

        def records():
            for seq, value in zip(indexes + 1, ravel[indexes]):
                yield '{}\t{}\t{}\n'.format(taxonkey, seq, value)

        f = IteratorFile(records())
        cursor.copy_from(f, 'taxon_distribution', columns=('taxon_key', 'cell_id', 'relative_abundance'))

        # update log. Postgres doesn't have UPSERT until 9.5
        # This might not be totally thread safe, see
        # master.lookup_* functions in integration-database
        # for other solutions

        cursor.execute("UPDATE taxon_distribution_log SET modified_timestamp=%s WHERE taxon_key=%s", (datetime.now(), taxonkey))
        if cursor.rowcount == 0:
            # UPDATE didn't find anything, so INSERT
            logger.debug('inserting new row in taxon_distribution_log')
            cursor.execute("""
                INSERT INTO taxon_distribution_log (taxon_key, modified_timestamp)
                VALUES (%s, %s)
                """, (taxonkey, datetime.now()))
        else:
            logger.debug('updated taxon_distribution_log')

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
