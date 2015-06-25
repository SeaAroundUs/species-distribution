import functools
import math
import operator

import numpy as np

from species_distribution.filters.filter import BaseFilter
from species_distribution.models.db import session
from species_distribution.models.taxa import TaxonHabitat
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
    mask = (kernel < a.data[_slice]) | kernel.mask

    a[_slice][~mask] = kernel[~mask]
    a.mask[_slice][~mask] = False
    # a[_slice][~mask] = kernel[~mask]

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

    def calculate_matrix(self, habitat_grid, effective_distance):
        """given a habitat_grid containing global habitat fractions
        and an effective_distance in km, returns a distribution matrix
        for that habitat

        The standard 1/2 degree grid is broken into finer resolution
        so the conical frustum kernel can be applied to each cell
        """

        # bump up resolution
        resolution_scale = 10

        grid = Grid()

        # total_area = grid.get_grid('TArea')

        # Estimate the distance been centroid and cell boundary
        # D = np.sqrt(total_area) / 2

        matrix = self.get_probability_matrix()
        new_size = np.multiply(matrix.shape, resolution_scale)
        high_resolution_matrix = np.ma.resize(matrix, new_size)
        radii = resolution_scale * np.sqrt(habitat_grid / np.pi)

        for i, j in np.ndindex(matrix.shape):
            if not habitat_grid[i, j] > 0:
                continue

            if i < 10 or j < 10 or i > 340 or j > 700:
                continue
            # r1 and r2 are in units of (higher resolution) grid cells

            # only handle centered square kernels now.
            # At high latitudes, this simplification won't be valid.
            # FIXME: using longitudinal length for cell size estimate for now.
            cell_length = grid.cell_height[i, j]

            # Radius of the circular habitat
            r2 = radii[i, j]
            # radius of the effective distance from the edge of the habitat
            r1 = resolution_scale * math.ceil((r2 + effective_distance * 1000) / cell_length)

            kernel = conical_frustum_kernel(r1, r2)

            # merge the kernel into to the high resolution matrix
            ii = i * resolution_scale + kernel.shape[0] // 2
            jj = j * resolution_scale + kernel.shape[1] // 2

            apply_kernel_greater_than(high_resolution_matrix, ii, jj, kernel)
            # alpha = (1 - d1 / habitat.EffectiveD).clip(0, 1)
            # habitat_effect = weight * alpha * (habitat_grid / total_area)
            # ma = np.ma.MaskedArray(data=habitat_effect, mask=(land_mask))

        # downscale high resolution matrix
        matrix = self._rebin(high_resolution_matrix, matrix.shape)
        return matrix

    def _filter(self, taxon):

        sesh = session()
        taxon_habitat = sesh.query(TaxonHabitat).filter_by(TaxonKey=taxon.taxonkey).one()
        # sesh.close()

        habitats = [
            # {'habitat_attr': 'Inshore', 'world_attr': 'Inshore'},
            # {'habitat_attr': 'Offshore', 'world_attr': 'Offshore'},

            # {'habitat_attr': 'Others', 'world_attr': 'Area'},
            {'habitat_attr': 'Coral', 'world_attr': 'Coral'},
            # {'habitat_attr': 'Estuaries', 'world_attr': 'Estuary'},
            # {'habitat_attr': 'Seagrass', 'world_attr': 'Seagrass'},
            # {'habitat_attr': 'Seamount', 'world_attr': 'Seamount'},
            # {'habitat_attr': 'Shelf', 'world_attr': 'Shelf'},
            # {'habitat_attr': 'Slope', 'world_attr': 'Slope'},
            # {'habitat_attr': 'Abyssal', 'world_attr': 'Abyssal'},
        ]

        probability_matrix = self.get_probability_matrix()

        grid = Grid()
        # land_mask = grid.get_grid('PWater') == 0

        matrices = []

        for hab in habitats:

            weight = getattr(taxon_habitat, hab['habitat_attr'])

            if not weight > 0:
                continue

            habitat_grid = grid.get_grid(hab['world_attr'])

            matrix = self.calculate_matrix(habitat_grid, taxon_habitat.EffectiveD)

            matrices.append(matrix)

        # combine and normalize:
        if len(matrices) > 0:
            probability_matrix = functools.reduce(operator.add, matrices)
            probability_matrix /= probability_matrix.max()
            return probability_matrix
        else:
            # empty
            return self.get_probability_matrix()
