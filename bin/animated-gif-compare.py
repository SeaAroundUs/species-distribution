#!/usr/bin/env python


""" creates animated GIFs of each taxon distribution from old and new distribution hdf5 files, and generates an
index.html for comparison """

import os

import h5py
import matplotlib.pyplot as plt
from matplotlib import animation


def animate(nframe):
    plt.cla()
    plt.imshow(grids[nframe])
    plt.title(nframe)

archive = h5py.File('archive-species-distribution.hdf5', 'r')
distribution = h5py.File('species-distribution.hdf5', 'r')

taxa = distribution['taxa'].keys()

with open('gifs/index.html', 'w') as index:

    index.write('<html><body>')
    for taxon in taxa:
        print(taxon)
        gif_name = 'gifs/' + str(taxon) + '.gif'
        if os.path.isfile(gif_name):
            print("{} exists, skipping".format(gif_name))
            continue

        try:
            grids = []
            grids.append(archive['taxa/' + str(taxon)])
            grids.append(distribution['taxa/' + str(taxon)])
        except KeyError:
            print("{} doesn't exist in archive".format(taxon))
            continue

        fig = plt.figure(figsize=(20, 16))
        anim = animation.FuncAnimation(fig, animate, frames=2)
        anim.save(gif_name, writer='imagemagick', fps=2)
        plt.close()
        index.write('<img title="{}" style="float: left;" src="{}"><br />'.format(str(taxon), str(taxon) + '.gif'))

    index.write('</body></html>')
