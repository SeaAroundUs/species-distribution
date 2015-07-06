#!/usr/bin/env python


""" transforms the taxon distribution table generated by the original SpecDisBuilder tool
into an hdf5 file for analysis """

import h5py
import numpy as np

from species_distribution.models.db import engine


def create_hdf5(fname, table_name):
    distribution_file = h5py.File(fname, 'w')

    distribution_file.create_group('taxa')

    distribution_file['latitude'] = np.arange(89.75, -90, -.5)
    distribution_file['longitude'] = np.arange(-179.75, 180, .5)

    with engine.connect() as connection:
        # get raw connection
        raw_conn = connection.connection.connection
        cursor = raw_conn.cursor()
        cursor.execute('SELECT DISTINCT taxonkey FROM {} ORDER BY taxonkey'.format(table_name))

        for taxonkey in cursor:
            taxonkey = taxonkey[0]
            print("key: {}".format(taxonkey))

            cursor2 = raw_conn.cursor()
            cursor2.execute('select cellid-1, relativeabundance from {} where taxonkey=%s ORDER BY cellid'.format(table_name), (taxonkey,))
            # create a grid populated with null values, then define values where cellid exists
            x, y = map(np.array, zip(*cursor2))
            data = np.full(360 * 720, np.nan)
            data[x] = y
            grid = data.reshape((360, 720))

            dataset = distribution_file.create_dataset('taxa/' + str(taxonkey), data=grid)

            dataset.dims[0].attach_scale(distribution_file['latitude'])
            dataset.dims[1].attach_scale(distribution_file['longitude'])

    distribution_file.close()

create_hdf5('archive-species-distribution.hdf5', 'taxon_distribution_archive')
create_hdf5('species-distribution.hdf5', 'taxon_distribution')
