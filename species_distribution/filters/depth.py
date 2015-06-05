import numpy as np

from species_distribution.filters.filter import Filter


class DepthFilter(Filter):

    def _filter(self, taxon):

        water_min_depth = self.grid.get_grid('EleMin')
        water_max_depth = self.grid.get_grid('EleMax')

        # combine grids into one array
        depth = np.dstack((water_min_depth, water_max_depth))

        mindepth = -taxon.mindepth
        maxdepth = -taxon.maxdepth

        mask = ((depth[0] <= mindepth) & (depth[0] >= maxdepth))  \
            | ((depth[1] <= mindepth) & (depth[1] >= maxdepth)) \
            | ((depth[0] <= mindepth) & (depth[1] >= maxdepth))

        probability_matrix = self.get_probability_matrix()

        probability_matrix[mask] = 1.0

        return probability_matrix


_f = DepthFilter()


def filter(*args):
    return _f.filter(*args)
