import functools
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


def conical_frustrum_kernel(r1, r2):
    """returns a square numpy array of side r1*2+1 containing a centered 0.0-1.0 density
    map of a conical frustrum with inner (smaller) radius r2 and outer (larger) radius r1"""

    xx, yy = np.mgrid[-r1:r1 + 1, -r1:r1 + 1]
    cone = (xx ** 2 + yy ** 2)
    kernel = np.ma.MaskedArray(data=cone, dtype=np.float)
    # mask values outside r1
    kernel.mask = cone > (r1 ** 2)

    # set values < r2 to maximum normalized output
    r2_mask = (cone <= (r2 ** 2))
    kernel[r2_mask] = r2 ** 2
    # normalize and invert
    kernel = (kernel - r2 ** 2) / kernel.max()
    kernel = 1 - kernel
    return kernel


class Filter(BaseFilter):

    def versatility(self, taxon):
        """ membership function for versatility.  14-4.pdf pp. 32 """
        return MembershipFunction((.25, .5, .5, .75))

    def maximum_length(self, taxon):
        """ membership function for maximum length.  14-4.pdf pp. 32 """
        return MembershipFunction((25, 50, 100, 150))

    def _filter(self, taxon):

        sesh = session()
        habitat = sesh.query(TaxonHabitat).filter_by(TaxonKey=taxon.taxonkey).one()
        # sesh.close()

        habitats = [
            # {'habitat_attr': 'Inshore', 'world_attr': 'Inshore'},
            # {'habitat_attr': 'Offshore', 'world_attr': 'Offshore'},

            {'habitat_attr': 'Others', 'world_attr': 'Area'},
            {'habitat_attr': 'Coral', 'world_attr': 'Coral'},
            {'habitat_attr': 'Estuaries', 'world_attr': 'Estuary'},
            # {'habitat_attr': 'Seagrass', 'world_attr': 'Seagrass'},
            {'habitat_attr': 'Seamount', 'world_attr': 'Seamount'},
            # {'habitat_attr': 'Shelf', 'world_attr': 'Shelf'},
            # {'habitat_attr': 'Slope', 'world_attr': 'Slope'},
            # {'habitat_attr': 'Abyssal', 'world_attr': 'Abyssal'},
        ]

        probability_matrix = self.get_probability_matrix()
        grid = Grid()

        total_area = grid.get_grid('TArea')
        land_mask = grid.get_grid('PWater') == 0

        # Estimate the distance been centroid and cell boundary
        D = np.sqrt(total_area) / 2

        matrices = []

        for hab in habitats:

            weight = getattr(habitat, hab['habitat_attr'])

            if not weight > 0:
                continue

            habitat_grid = grid.get_grid(hab['world_attr'])

            # Estimate the radius of the habitat, assuming it is circular in shape
            R = np.sqrt(habitat_grid / np.pi)

            # 'Estimate the distance between cell boundary and boundary of habitat
            d1 = (D - R).clip(0)

            alpha = (1 - d1 / habitat.EffectiveD).clip(0, 1)
            habitat_effect = weight * alpha * (habitat_grid / total_area)
            ma = np.ma.MaskedArray(data=habitat_effect, mask=(land_mask))
            if ma.sum() > 0:
                matrices.append(ma)

        # combine and normalize:
        if len(matrices) > 0:
            probability_matrix = functools.reduce(operator.add, matrices)
            probability_matrix /= probability_matrix.max()
            return probability_matrix
        else:
            # empty
            return self.get_probability_matrix()
