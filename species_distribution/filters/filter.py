import numpy as np

from species_distribution.models.world import Grid


class Filter():
    def __init__(self):
        self.grid = Grid()
        self.probability_matrix = self.get_probability_matrix(self.grid.shape)

    def get_probability_matrix(self, shape):
        return np.ma.MaskedArray(data=np.zeros(shape), mask=True, dtype=float)
