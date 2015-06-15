from species_distribution.filters.filter import BaseFilter


class Filter(BaseFilter):

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
        probability_matrix = self.get_probability_matrix()
        probability_matrix[mask] = 1.0

        return probability_matrix
