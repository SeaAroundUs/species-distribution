#!/usr/bin/env python

""" dev tool to display raster images of grids from the Grid table """

import h5py
from PIL import Image

f = h5py.File('species-distribution.hdf5')
for key in f.keys():
    arr = f.get(key).value
    if arr.sum() > 0:
        print(key)
        arr *= 255
        # arr = arr.astype('int')
        im = Image.fromarray(arr)
        im.save('/tmp/im/' + key + '.tiff')
