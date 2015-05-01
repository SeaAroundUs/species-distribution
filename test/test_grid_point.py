import unittest2

from species_distribution.models.db import session
from species_distribution.models.world import Grid, GridPoint


class TestGridPoint(unittest2.TestCase):

    def test_grid_point(self):
        seq = 246157
        grid_point = session().query(GridPoint).get(seq)
        self.assertEqual(342, grid_point.Row)
        self.assertEqual(637, grid_point.Col)

    def test_grid_shape(self):
        grid = Grid().get_grid(field='SST')
        self.assertEqual((360, 720), grid.shape)

    def test_grid(self):
        grid = Grid()
        self.assertEqual((360, 720), grid.shape)

    def test_grid_value(self):
        grid = Grid().get_grid(field='SST')
        self.assertEqual(-1.79, grid[0][0])
