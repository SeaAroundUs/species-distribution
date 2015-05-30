"""Filters which accept a distribution matrix, and return a modified matrix"""

import logging

import numpy as np

from species_distribution.models.db import engine
from species_distribution.models.world import Grid
from species_distribution.filters.filter import Filter
from species_distribution import exceptions

logger = logging.getLogger(__name__)


def get_cells_for_taxon(taxon):
    query = """
    SELECT seq, row, col
    FROM grid g, distribution d
    WHERE ST_INTERSECTS(g.geom, d.geom)
        AND taxon=%s
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

        for seq, row, col in get_cells_for_taxon(taxon):

            self.probability_matrix[row - 1][col - 1] = 1.0

        return self.probability_matrix


def filter(*args):
    f = PolygonFilter()
    return f.filter(*args)
