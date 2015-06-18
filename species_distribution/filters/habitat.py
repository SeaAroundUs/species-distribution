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


class Filter(BaseFilter):

    def versatility(self, taxon):
        """ membership function for versatility.  14-4.pdf pp. 32 """
        versatility_function = MembershipFunction((.25, .5, .5, .75))

    def maximum_length(self, taxon):
        """ membership function for maximum length.  14-4.pdf pp. 32 """
        maximum_length_function = MembershipFunction((25, 50, 100, 150))

    def _filter(self, taxon):

        sesh = session()
        habitat = sesh.query(TaxonHabitat).filter_by(TaxonKey=taxon.taxonkey).one()
        # sesh.close()

        habitats = [
            # {'habitat_attr': 'Inshore', 'world_attr': 'Inshore'},
            # {'habitat_attr': 'Offshore', 'world_attr': 'Offshore'},

            # {'habitat_attr': 'Others', 'world_attr': 'Area'}, # taxaDistribution.vb:2438
            {'habitat_attr': 'Coral', 'world_attr': 'Coral'},
            {'habitat_attr': 'Estuaries', 'world_attr': 'Estuary'},
            {'habitat_attr': 'Seamount', 'world_attr': 'Seamount'},
            {'habitat_attr': 'Shelf', 'world_attr': 'Shelf'},
            {'habitat_attr': 'Slope', 'world_attr': 'Slope'},
            {'habitat_attr': 'Abyssal', 'world_attr': 'Abyssal'},
        ]

        probability_matrix = self.get_probability_matrix()
        grid = Grid()

        # total_abundance = 0
        # habitat_area = grid.area_coast
        # weight = habitat.Inshore
        # taxaDistribution.vb: 2155
        # area_ratio = (habitat_area / total_area)
        # x = area_ratio + (1 - area_ratio) * habitat_effect
        # y = x + (1 - x) * habitat_effect1  # and for habitat_effect1, the neighbor cells?
        # total_abundance = habitat_effect * weight + total_abundance

        # habitat_area = grid.area_offshore
        # weight = habitat.Offshore
        # contribution = (habitat_area / total_area) * weight
        # probability_matrix += contribution

        total_area = grid.get_grid('TArea')

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
            ma = np.ma.MaskedArray(data=habitat_effect, mask=False)
            if ma.sum() > 0:
                matrices.append(ma)

        # combine and normalize:
        if len(matrices) > 0:
            probability_matrix = functools.reduce(operator.mul, matrices)
            # probability_matrix /= probability_matrix.max()
            return probability_matrix
        else:
            # empty
            return self.get_probability_matrix()
