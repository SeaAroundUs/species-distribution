import unittest2

from species_distribution.models.db import Session
from species_distribution.models.world import Grid, GridPoint


class TestGridPoint(unittest2.TestCase):

    def test_grid_point(self):
        seq = 246157
        with Session() as session:
            grid_point = session.query(GridPoint).get(seq)
            self.assertEqual(342, grid_point.cell_row)
            self.assertEqual(637, grid_point.cell_col)

    def test_grid_shape(self):
        grid = Grid().get_grid(field='sst')
        self.assertEqual((360, 720), grid.shape)

    def test_grid(self):
        grid = Grid()
        self.assertEqual((360, 720), grid.shape)

    def test_grid_value(self):
        grid = Grid().get_grid(field='sst')
        self.assertEqual(-1.79, grid[0, 0])

    def test_derived_field_area_coast(self):
        grid = Grid().area_coast
        self.assertEqual(0.0, grid[0, 0])

    def test_derived_field_area_offshore(self):
        grid = Grid().area_offshore
        self.assertEqual(13.48, grid[0, 0])
