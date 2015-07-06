import functools
import math
import operator

import numpy as np

from species_distribution.filters.filter import BaseFilter
from species_distribution.filters.polygon import Filter as PolygonFilter
from species_distribution.models.taxa import Taxon, TaxonHabitat
from species_distribution.models.world import Grid


class MembershipFunction():
    """ give break points for 3 membership categories:
    e.g. [[25, 50, 100, 150]]"""

    def __init__(self, break_points):
        self.break_points = (0, ) + tuple(break_points)

    def values(self, value):
        return self.low(value), self.middle(value), self.high(value)

    def low(self, value):
        y_coords = (1, 1, 0, 0, 0)
        return np.interp(value, self.break_points, y_coords)

    def middle(self, value):
        y_coords = (0, 0, 1, 1, 0)
        return np.interp(value, self.break_points, y_coords)

    def high(self, value):
        y_coords = (0, 0, 0, 0, 1)
        return np.interp(value, self.break_points, y_coords)


@functools.lru_cache(maxsize=10 ** 3)
def conical_frustum_kernel(r1, r2):
    """returns a square numpy array of side r1*2+1 containing a centered 0.0-1.0 density
    map of a conical frustum with inner (smaller) radius r2 and outer (larger) radius r1"""

    xx, yy = np.mgrid[-r1:r1 + 1, -r1:r1 + 1]
    cone = (xx ** 2 + yy ** 2)
    kernel = np.ma.MaskedArray(data=cone, dtype=np.float)
    # mask values outside r1
    mask = kernel > (r1 ** 2)
    kernel.mask = mask

    # set values < r2 to maximum normalized output
    r2_mask = (kernel <= (r2 ** 2))
    kernel[r2_mask] = r2 ** 2
    # normalize and invert
    kernel = (kernel - r2 ** 2) / kernel.max()
    kernel = 1 - kernel
    return kernel


def apply_kernel_greater_than(a, i, j, kernel):
    """
    applies kernel to array a at location i, j
    where kernel > array and returns a
    reference to the modified array a.

    kernel should be square with odd side lengths
    so it can be applied symmetrically at i, j
    """

    y = i - kernel.shape[0] // 2
    x = j - kernel.shape[1] // 2

    _slice = np.index_exp[y:y + kernel.shape[0], x:x + kernel.shape[1]]

    # mask out values which are already higher than kernel would provide,
    # or are masked in the kernel
    mask = (kernel < a[_slice]) | kernel.mask
    a[_slice][~mask] = kernel[~mask]
    a.mask[_slice][~mask] = False
    return a


class Filter(BaseFilter):

    def versatility(self, taxon):
        """ membership function for versatility.  14-4.pdf pp. 32 """
        return MembershipFunction((.25, .5, .5, .75))

    def maximum_length(self, taxon):
        """ membership function for maximum length.  14-4.pdf pp. 32 """
        return MembershipFunction((25, 50, 100, 150))

    def _rebin(self, a, shape):
        """ return a new array which has been rebinned to the new shape """

        # tip of the hat to JF Sebastian:
        # http://stackoverflow.com/a/8090605/958118
        sh = shape[0], a.shape[0] // shape[0], shape[1], a.shape[1] // shape[1]
        return a.reshape(sh).mean(-1).mean(1)

    def calculate_matrix(self, taxon, habitat_grid, effective_distance, session=None):
        """given a habitat_grid containing global habitat fractions
        and an effective_distance in km, returns a distribution matrix
        for that habitat

        The standard 1/2 degree grid is broken into finer resolution
        so the conical frustum kernel can be applied to each cell
        """

        grid = Grid()
        total_area = grid.get_grid('TArea') * 10 ** 6  # meters**2
        matrix = self.get_probability_matrix()

        # bump up resolution by this factor for calculations
        resolution_scale = 10

        new_size = np.multiply(matrix.shape, resolution_scale)
        high_resolution_matrix = np.ma.resize(matrix, new_size)

        habitat_radius_m = np.sqrt(habitat_grid * total_area / np.pi)
        cell_length_m = np.sqrt(total_area)

        # use polygon matrix to reduce the number of cells to calculate
        polygon_matrix = PolygonFilter()._filter(taxon=taxon, session=session)

        for i, j in np.ndindex(matrix.shape):
            if (not habitat_grid[i, j] > 0):
                continue
            if polygon_matrix.mask[i, j]:
                continue

            edge_padding = 20
            if i < edge_padding \
                or j < edge_padding \
                or i > (matrix.shape[0] - edge_padding) \
                    or j > (matrix.shape[1] - edge_padding):

                continue

            try:

                # only handle centered square kernels now.
                # At high latitudes, this simplification won't be valid.
                # assuming square for now.
                cell_length = cell_length_m[i, j]

                # r1 and r2 are in units of (higher resolution) grid cells
                # Radius of the circular habitat
                r2 = math.ceil(resolution_scale * habitat_radius_m[i, j] / cell_length)
                # radius of the effective distance from the edge of the habitat
                r1 = math.ceil(r2 + resolution_scale * effective_distance / cell_length)

                kernel = conical_frustum_kernel(r1, r2)
                # merge the kernel into to the high resolution matrix
                ii = i * resolution_scale + kernel.shape[0] // 2
                jj = j * resolution_scale + kernel.shape[1] // 2
                apply_kernel_greater_than(high_resolution_matrix, ii, jj, kernel)

            except ValueError as e:
                self.logger.info('skipping cell [{}, {}]. r1: {} r2: {}  value error: {}'.format(i, j, r1, r2, str(e)))

        # downscale high resolution matrix
        matrix = self._rebin(high_resolution_matrix, matrix.shape)
        return matrix

    def combine_matrices(self, matrices, dist_independent_matrices, taxon_habitat):
        """combine matrices and normalize"""

        grid = Grid()

        # filter out inshore/offshore
        distance_independent_probability_matrix = functools.reduce(operator.add, dist_independent_matrices)
        coastal_prop = grid.get_grid('CoastalProp')
        if taxon_habitat.Inshore == 0:
            mask = coastal_prop == 1
            # if a cell has a value set by a distance independent filter already, don't mask it,
            # else mask it
            distance_independent_probability_matrix.mask = distance_independent_probability_matrix.mask & mask

        if taxon_habitat.Offshore == 0:
            mask = coastal_prop == 0
            distance_independent_probability_matrix.mask = distance_independent_probability_matrix.mask & mask

        probability_matrix = functools.reduce(operator.add, matrices + distance_independent_probability_matrix)
        probability_matrix /= probability_matrix.max()
        return probability_matrix

    def _filter(self, taxon=None, session=None):

        habitats = [
            {'habitat_attr': 'Inshore', 'world_attr': 'area_coast', 'dist_independant': False},
            {'habitat_attr': 'Offshore', 'world_attr': 'area_offshore', 'dist_independant': False},
            {'habitat_attr': 'Others', 'world_attr': 'water_area', 'dist_independant': False},
            {'habitat_attr': 'Coral', 'world_attr': 'Coral', 'dist_independant': True},
            {'habitat_attr': 'Estuaries', 'world_attr': 'Estuary', 'dist_independant': False},
            # {'habitat_attr': 'Seagrass', 'world_attr': 'Seagrass', 'dist_independant': True},
            {'habitat_attr': 'Seamount', 'world_attr': 'Seamount', 'dist_independant': False},
            {'habitat_attr': 'Shelf', 'world_attr': 'Shelf', 'dist_independant': False},
            {'habitat_attr': 'Slope', 'world_attr': 'Slope', 'dist_independant': False},
            {'habitat_attr': 'Abyssal', 'world_attr': 'Abyssal', 'dist_independant': False},
        ]

        probability_matrix = self.get_probability_matrix()

        grid = Grid()

        matrices = []
        dist_independent_matrices = []

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxonkey)

        for hab in habitats:

            weight = getattr(taxon_habitat, hab['habitat_attr'])

            if not weight > 0:
                continue

            habitat_grid = grid.get_grid(hab['world_attr'])
            if hab['world_attr'] in ('area_offshore', 'area_coast', 'water_area', 'Shelf', 'Slope', 'Abyssal'):
                # Area is in km2, convert to percentage
                total_area = grid.get_grid('TArea')
                habitat_grid = habitat_grid / total_area

            matrix = self.calculate_matrix(taxon, habitat_grid, taxon_habitat.EffectiveD, session=session)
            matrix *= weight
            matrix *= habitat_grid
            if hab['dist_independant']:
                dist_independent_matrices.append(matrix)
            else:
                matrices.append(matrix)

        if len(matrices) > 0:
            probability_matrix = self.combine_matrices(matrices, dist_independent_matrices, taxon_habitat)
            return probability_matrix
        else:
            # empty
            return self.get_probability_matrix()
