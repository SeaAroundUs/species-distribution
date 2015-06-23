#!/usr/bin/env python

""" dev tool to display raster images of grids from the Grid table """

import sys

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from species_distribution.models.world import Grid

grid = Grid()


def make_image(field):
    g = grid.get_grid(field=field)
    # Image.fromarray(g.astype('int32')).show()
    g = g / g.max()
    g = np.clip(g, 0, 1)
    array = plt.cm.jet(g) * 255
    array = array.astype(np.uint8)
    image = Image.fromarray(array)
    fname = 'png/world/{}.png'.format(field)
    image.save(fname)
    print('wrote {}'.format(fname))

try:
    field = sys.argv[1]
    make_image(field)
except IndexError:
    for field in Grid.field_names.__get__(grid):
        make_image(field)
