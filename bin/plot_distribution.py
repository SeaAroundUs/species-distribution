#!/usr/bin/env python

""" dev tool to display raster images of grids from the Grid table """

import h5py
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.misc import imresize

f = h5py.File('species-distribution.hdf5')
for key in f['taxa'].keys():
    print(key)

    array = f['taxa'].get(key).value[:]
    alpha = array.copy()
    mask = alpha > 0
    alpha = alpha.astype(np.uint8)
    alpha[~mask] = 0  # convert nans
    alpha[mask] = 255  # convert nans
    alpha = Image.fromarray(alpha, mode='L')
    array *= 255
    array = array.astype(np.uint8)

    # colorize
    # array = plt.cm.jet(array) * 255
    # array = array.astype(np.uint8)

    im = Image.fromarray(array)
    im.putalpha(alpha)
    im = im.resize((7200, 3600), Image.NEAREST)
    im.save('./' + key + '.tif')
    break
