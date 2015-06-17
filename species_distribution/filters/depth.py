import itertools

import numpy as np
from .filter import BaseFilter
from .polygon import Filter as PolygonFilter


class Filter(BaseFilter):
    """ Depth Filter

    probability_matrix values are defined where taxon min and max depth
    fall within the min and max depth of the cell.  Value is
    proportional to the amount falling within the scalene triangle
    distribution """
    def _filter(self, taxon):

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        world_depth = self.grid.get_grid('EleAvg')

        mindepth = -taxon.mindepth
        maxdepth = -taxon.maxdepth

        # get polygon distribution to reduce work done here
        polygon_distribution = PolygonFilter.filter(taxon)
        mask = (world_depth > mindepth) | (world_depth >= 0) | polygon_distribution.mask

        # create scalene triangle properties
        one_third_depth = mindepth - (mindepth - maxdepth) / 3
        # area of triangle is 1/2 * base * height.
        # height = 1 (maximum probability), so just base / 2
        triangle_area = (mindepth - maxdepth) / 2
        xp = [maxdepth, one_third_depth, mindepth]
        fp = [0, 1, 0]

        probability_matrix = self.get_probability_matrix()

        # iterate over the valid values
        for i, j in np.ndindex(probability_matrix.shape):
            if mask[i, j]:
                continue

            depth = world_depth[i, j]
            interpolated_value = np.interp([depth], xp, fp)[0]

            # create list of (Z,P) tuples where Z = depth and P = probabilty
            # order by depth, and cast out everything outside the world range
            # what is left can be integrated and divided by total area to get
            # cell probability

            ZP = sorted(itertools.chain(zip(xp, fp), ((depth, interpolated_value),)))
            ZP_in_range = list(filter(lambda x: x[0] >= depth, ZP))
            x, y = zip(*ZP_in_range)
            P = np.trapz(y, x) / triangle_area

            probability_matrix[i, j] = P

        return probability_matrix
