"""Filters which accept a distribution matrix, and return a modified matrix"""

import logging

from species_distribution.models.db import engine
from species_distribution.filters.filter import Filter
from species_distribution import exceptions

logger = logging.getLogger(__name__)


def get_cells_for_taxon(taxon):

    query = """
    WITH dis AS (
        SELECT ST_SIMPLIFY(geom,.25) as geom FROM distribution
        WHERE taxon=%s
    )
    SELECT g.row-1, g.col-1
        FROM grid g
         JOIN dis d ON (1=1)
        WHERE ST_INTERSECTS(g.geom, d.geom)

    """

    with engine.connect() as conn:
        result = conn.execute(query, taxon.taxonkey)
        data = result.fetchall()
        if len(data) == 0:
            raise exceptions.NoPolygonException
        else:
            logger.debug('Found {} matching cells'.format(len(data)))
        return data


class PolygonFilter(Filter):

    def filter(self, taxon):
        """ sets probability to 1.0 for every grid cell which intersects
        the taxon distribution defined in the distribution geometries.
        Modifies and returns distribution_matrix"""

        logger.debug('generating polygon probability matrix')

        cells = get_cells_for_taxon(taxon)

        # use numpy advanced indexing to set all records of (row,col) to 1
        indexes = list(zip(*cells))
        self.probability_matrix[indexes[0], indexes[1]] = 1.0

        return self.probability_matrix


def filter(*args):
    f = PolygonFilter()
    return f.filter(*args)
