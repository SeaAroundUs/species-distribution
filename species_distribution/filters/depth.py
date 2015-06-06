import numpy as np

from species_distribution.filters.filter import Filter


class DepthFilter(Filter):

    def _filter(self, taxon):

        # min and max are inverted between taxon and world
        water_max_depth = self.grid.get_grid('EleMin')
        water_min_depth = self.grid.get_grid('EleMax')

        # combine grids into one array
        depth = np.dstack((water_min_depth, water_max_depth))

        mindepth = -taxon.mindepth
        maxdepth = -taxon.maxdepth

        # exclude cells outside taxon depth range
        mask = ~((depth[:, :, 0] < maxdepth) | (depth[:, :, 1] > mindepth))
        probability_matrix = self.get_probability_matrix()

        probability_matrix[mask] = 1.0

        return probability_matrix


_f = DepthFilter()


def filter(*args):
    return _f.filter(*args)
