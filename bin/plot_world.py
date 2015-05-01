#!/usr/bin/env python

""" dev tool to display raster images of grids from the Grid table """

from PIL import Image

from species_distribution.models.world import Grid

grid = Grid()

for field in ('Elevation_Mean', 'SST', 'Seamount', 'PPAnnual', 'Coral', 'Bathy_Min'):
    g = grid.get_grid(field=field)
    Image.fromarray(g).show()
    input("field: {} <press enter to continue>".format(field))
