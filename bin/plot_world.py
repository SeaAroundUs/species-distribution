#!/usr/bin/env python

""" dev tool to display raster images of grids from the Grid table """

import sys

from PIL import Image

from species_distribution.models.world import Grid

grid = Grid()

field = sys.argv[1]

g = grid.get_grid(field=field)
Image.fromarray(g.astype('int32')).show()
