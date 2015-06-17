import numpy as np
from species_distribution.filters.filter import BaseFilter


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

        world_mindepth = self.grid.get_grid('EleMax')
        world_maxdepth = self.grid.get_grid('EleMin')

        mindepth = -taxon.mindepth
        maxdepth = -taxon.maxdepth

        # exclude cells outside taxon depth range
        mask = ~((world_mindepth < maxdepth) | (world_maxdepth > mindepth))

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
            if not mask[i, j]:
                continue

            world_depths = [world_maxdepth[i, j], world_mindepth[i, j]]
            interpolated_values = np.interp(world_depths, xp, fp)

            # create list of (Z,P) tuples where Z = depth and P = probabilty
            # order by depth, and cast out everything outside the world range
            # what is left can be integrated and divided by total area to get
            # cell probability

            ZP = sorted(list(zip(xp, fp)) + list(zip(world_depths, interpolated_values)))
            ZP_in_range = list(filter(lambda x: x[0] >= world_depths[0] and x[0] <= world_depths[1], ZP))
            x, y = zip(*ZP_in_range)
            P = np.trapz(y, x) / triangle_area

            probability_matrix[i, j] = P

        return probability_matrix
