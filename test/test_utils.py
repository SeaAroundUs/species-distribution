import unittest2

import numpy as np

from species_distribution import utils


class TestUtils(unittest2.TestCase):

    def test_iterator_to_file_read_n_bytes(self):
        it = (str(x) for x in range(3))
        f = utils.IteratorFile(it)

        actual = f.read(2)
        expected = '01'
        self.assertEqual(expected, actual)

    def test_iterator_to_file_read_all_bytes(self):
        it = (str(x) for x in range(3))
        f = utils.IteratorFile(it)

        actual = f.read()
        expected = '012'
        self.assertEqual(expected, actual)

    def test_iterator_to_file_data_larger_than_chunk_size(self):
        it = (str(x) * 5 for x in range(1))
        f = utils.IteratorFile(it)
        f.read(2)
        actual = f.read(2)
        expected = '00'
        self.assertEqual(expected, actual)

        actual = f.read(2)
        expected = '0'
        self.assertEqual(expected, actual)

    def test_combine_probability_matrices(self):
        m1 = np.ma.MaskedArray(np.full((2, 2), np.nan), mask=True)
        m2 = np.ma.MaskedArray(np.full((2, 2), np.nan), mask=True)

        m1[0, 0] = .5
        m2[0, 0] = .1
        m2[0, 1] = .1

        result = utils.combine_probability_matrices((m1, m2))

        self.assertAlmostEqual(result[0, 0], .05)
        self.assertFalse(result[0, 1])
