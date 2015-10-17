import functools

import numpy as np

from species_distribution import sd_io as io
from species_distribution import settings
from species_distribution.filters.filter import BaseFilter
from species_distribution.filters.polygon import Filter as PolygonFilter
from species_distribution.models.taxa import TaxonHabitat
from species_distribution.models.world import Grid


@functools.lru_cache(maxsize=None)
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


def merge_kernel_greater_than(a, x, y, kernel):
    """ merges kernel into a at x,y.  Doesn't handle edge wrapping"""

    # mask out values which are already higher than kernel would provide,
    # or are masked in the kernel

    _slice = np.index_exp[y:y + kernel.shape[0], x:x + kernel.shape[1]]
    view = a[_slice]
    mask = (kernel < view) | kernel.mask
    np.ma.putmask(view, ~mask, kernel)


def apply_kernel_greater_than(a, i, j, kernel):
    """
    applies kernel to array a at location i, j
    where kernel > array and returns a
    reference to the modified array a.

    kernel application is wrapped around the array horizontally

    kernel should be square with odd side lengths
    so it can be applied symmetrically at i, j
    """

    y = i - kernel.shape[0] // 2
    x = j - kernel.shape[1] // 2

    rbound = x + kernel.shape[1]

    if x < 0 or rbound > a.shape[1]:

        if x < 0:
            # extends beyond left boundary,
            # move over to other side to treat both
            # out of bounds cases the same
            x = a.shape[1] + x
            rbound = x + kernel.shape[1]

        # extending beyond right boundary
        extra = rbound - a.shape[1]
        # merge into right side
        merge_kernel_greater_than(a, x, y, kernel[:, 0:kernel.shape[1] - extra])
        # then left
        merge_kernel_greater_than(a, 0, y, kernel[:, kernel.shape[1] - extra: kernel.shape[1]])

    else:
        merge_kernel_greater_than(a, x, y, kernel)
    return a


class Filter(BaseFilter):

    def _rebin(self, a, shape):
        """ return a new array which has been rebinned to the new shape """

        # tip of the hat to JF Sebastian:
        # http://stackoverflow.com/a/8090605/958118
        sh = shape[0], a.shape[0] // shape[0], shape[1], a.shape[1] // shape[1]
        return a.reshape(sh).mean(-1).mean(1)

    def calculate_matrix(self, taxon, habitat_grid, effective_distance, session=None, habitat_name=None):
        """given a habitat_grid containing global habitat fractions
        and an effective_distance in km, returns a distribution matrix
        for that habitat

        The standard 1/2 degree grid is broken into finer resolution
        so the conical frustum kernel can be applied to each cell
        """

        total_area = self.grid.get_grid('total_area') * 10 ** 6  # km**2 to meters**2
        matrix = self.get_probability_matrix()

        # bump up resolution by this factor for calculations
        resolution_scale = 10

        new_size = np.multiply(matrix.shape, resolution_scale)
        high_resolution_matrix = np.ma.resize(matrix, new_size)

        habitat_radius_m = np.sqrt(habitat_grid * total_area / np.pi)
        cell_length_m = np.sqrt(total_area)

        # only handle centered square kernels now.
        # At high latitudes, this simplification won't be valid.
        # assuming square for now.
        # ell_length = cell_length_m[i, j]

        # r1 and r2 are in units of (higher resolution) grid cells
        # Radius of the circular habitat
        r2 = np.ceil(resolution_scale * habitat_radius_m / cell_length_m)
        # radius of the effective distance from the edge of the habitat
        r1 = np.ceil(r2 + resolution_scale * effective_distance * 1000 / cell_length_m)

        # use polygon matrix to reduce the number of cells to calculate
        polygon_matrix = PolygonFilter()._filter(taxon=taxon, session=session)

        edge_padding = 10

        for i, j in np.ndindex(matrix.shape[0] - edge_padding * 2, matrix.shape[1]):

            i += edge_padding

            if (not habitat_grid[i, j] > 0):
                continue
            if polygon_matrix.mask[i, j]:
                continue

            try:
                _r1 = r1[i, j]
                _r2 = r2[i, j]
                kernel = conical_frustum_kernel(_r1, _r2)
                # merge the kernel into to the high resolution matrix
                ii = i * resolution_scale + kernel.shape[0] // 2
                jj = j * resolution_scale + kernel.shape[1] // 2
                apply_kernel_greater_than(high_resolution_matrix, ii, jj, kernel)

            except ValueError as e:
                self.logger.debug('skipping cell [{}, {}]. r1: {} r2: {}  value error: {}'.format(i, j, r1, r2, str(e)))

        if settings.DEBUG:
            io.save_image(high_resolution_matrix, '{}-habitat-{}'.format(taxon.taxon_key, habitat_name))

        # downscale high resolution matrix
        matrix = self._rebin(high_resolution_matrix, matrix.shape)
        return matrix

    def combine_matrices(self, matrices, dist_independent_matrices, taxon_habitat):
        """combine matrices and normalize"""

        grid = Grid()

        probability_matrix = self.get_probability_matrix()

        # filter out inshore/offshore
        # distance_independent_probability_matrix = functools.reduce(operator.add, dist_independent_matrices)
        for matrix in dist_independent_matrices:
            probability_matrix.mask &= matrix.mask
            probability_matrix += matrix

        coastal_prop = grid.get_grid('coastal_prop')
        if taxon_habitat.inshore == 0:
            mask = coastal_prop == 1
            # if a cell has a value set by a distance independent filter already, don't mask it,
            # else mask it
            probability_matrix.mask &= mask

        if taxon_habitat.offshore == 0:
            mask = coastal_prop == 0
            probability_matrix.mask &= mask

        for matrix in matrices:
            mask = probability_matrix.mask & matrix.mask
            probability_matrix += matrix
            probability_matrix.mask = mask

        probability_matrix /= probability_matrix.max()
        return probability_matrix

    def _filter(self, taxon=None, session=None):

        habitats = [
            {'habitat_attr': 'inshore', 'world_attr': 'area_coast', 'dist_independant': False},
            {'habitat_attr': 'offshore', 'world_attr': 'area_offshore', 'dist_independant': False},
            {'habitat_attr': 'others', 'world_attr': 'percent_water', 'dist_independant': False},
            {'habitat_attr': 'coral', 'world_attr': 'coral', 'dist_independant': True},
            {'habitat_attr': 'estuaries', 'world_attr': 'estuary', 'dist_independant': False},
            # {'habitat_attr': 'Seagrass', 'world_attr': 'Seagrass', 'dist_independant': True},
            {'habitat_attr': 'sea_mount', 'world_attr': 'seamount', 'dist_independant': False},
            {'habitat_attr': 'shelf', 'world_attr': 'shelf', 'dist_independant': False},
            {'habitat_attr': 'slope', 'world_attr': 'slope', 'dist_independant': False},
            {'habitat_attr': 'abyssal', 'world_attr': 'abyssal', 'dist_independant': False},
        ]

        probability_matrix = self.get_probability_matrix()

        grid = Grid()

        matrices = []
        dist_independent_matrices = [self.get_probability_matrix()]  # seed it with an empty one in case no others exist

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxon_key)

        for hab in habitats:

            weight = getattr(taxon_habitat, hab['habitat_attr'])

            if not weight > 0:
                continue

            # if taxon.pelagic and hab['world_attr'] == 'seamount':
            #     self.logger.debug('skipping seamount habitat for pelagic taxon {}'.format(taxon.taxon_key))
            #     continue

            self.logger.debug('habitat: {}'.format(hab['habitat_attr']))

            habitat_grid = grid.get_grid(hab['world_attr'])
            if hab['world_attr'] in ('area_offshore', 'area_coast', 'estuary', 'shelf', 'slope', 'abyssal'):
                # Area is in km2, convert to percentage
                total_area = grid.get_grid('total_area')
                habitat_grid = habitat_grid / total_area
            if hab['world_attr'] in ('percent_water', 'seamount'):
                habitat_grid = habitat_grid / 100

            matrix = self.calculate_matrix(
                taxon,
                habitat_grid,
                taxon_habitat.effective_distance,
                session=session,
                habitat_name=hab['habitat_attr']
            )
            matrix *= weight
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
