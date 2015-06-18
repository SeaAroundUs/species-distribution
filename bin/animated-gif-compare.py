#!/usr/bin/env python


""" creates animated GIFs of each taxon distribution from old and new distribution hdf5 files, and generates an
index.html for comparison """

from multiprocessing import Pool
import os

import h5py


def process_taxon(gif_name, grids):
    import matplotlib.pyplot as plt
    from matplotlib import animation

    def animate(nframe):
        plt.cla()
        plt.imshow(grids[nframe])
        plt.title(nframe)

    fig = plt.figure(figsize=(10, 8))
    anim = animation.FuncAnimation(fig, animate, frames=2)
    anim.save(gif_name, writer='imagemagick', fps=2)
    plt.close()
    print("wrote {}".format(gif_name))

archive = h5py.File('archive-species-distribution.hdf5', 'r')
distribution = h5py.File('species-distribution.hdf5', 'r')

taxa = distribution['taxa'].keys()

pool = Pool(8)

with open('gifs/index.html', 'w') as index:

    index.write('<html><body>')
    for taxon in taxa:
        gif_name = 'gifs/' + str(taxon) + '.gif'
        index.write('<div style="float:left;"><span>{}</span><img title="{}" src="{}" /></div>'.format(str(taxon), str(taxon), str(taxon) + '.gif'))

        if os.path.isfile(gif_name):
            print("{} exists, skipping".format(gif_name))
            continue

        try:
            grids = []
            grids.append(archive['taxa/' + str(taxon)][:])
            grids.append(distribution['taxa/' + str(taxon)][:])
        except KeyError:
            print("{} doesn't exist in archive".format(taxon))
            continue

        pool.apply_async(process_taxon, [gif_name, grids])

    index.write('</body></html>')

pool.close()
pool.join()
