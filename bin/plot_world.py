#!/usr/bin/env python

""" dev tool to display raster images of grids from the Grid table """

from PIL import Image

from species_distribution.models.world import Grid

grid = Grid()

# for field in grid.field_names:
# for field in ('FAO',):
# for field in ('Area', 'TArea', 'Elevation_Mean', 'SST', 'PLand', 'EleMin', 'Seamount', 'PPAnnual', 'Coral', 'Bathy_Min'):
for field in ('PWater',):
    g = grid.get_grid(field=field)
    Image.fromarray(g.astype('int32')).show()
    input("field: {} <press enter to continue>".format(field))
