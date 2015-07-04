import unittest2

import numpy as np

import species_distribution.filters as filters


class TestHabitat(unittest2.TestCase):

    def test_membership_function(self):
        f = filters.habitat.MembershipFunction([25, 50, 100, 150])

        values = f.values(0)
        self.assertAlmostEqual(values[0], 1)
        self.assertAlmostEqual(values[1], 0)
        self.assertAlmostEqual(values[2], 0)

        values = f.values(125)
        self.assertAlmostEqual(values[0], 0)
        self.assertAlmostEqual(values[1], .5)
        self.assertAlmostEqual(values[2], .5)

        values = f.values(9999)
        self.assertAlmostEqual(values[0], 0)
        self.assertAlmostEqual(values[1], 0)
        self.assertAlmostEqual(values[2], 1)

    def test_filter(self):

        key = 690690
        distribution = filters.habitat.Filter.filter(taxon=key)
        self.assertEqual(distribution.shape, (360, 720))

    def test_frustum_kernel(self):
        r1 = 20
        r2 = 5
        kernel = filters.habitat.conical_frustum_kernel(r1, r2)
        self.assertEqual(kernel.shape, (r1 * 2 + 1, r1 * 2 + 1))
        self.assertFalse(kernel[0, 0], 'corner value should be masked')
        self.assertEqual(kernel[r1, r1], 1, 'center value is not 1')
        self.assertEqual(kernel[r1 + r2, r1], 1, 'value at r2 is not 1')
        self.assertTrue(kernel[r1 + r2 + 1, r1] < 1, 'value at r2 is not less than 1')

    def test_apply_kernel_greater_than(self):
        # create an array containing constant value .5
        # apply a kernel with gradient 0 to 1.
        # values in a should be preserved where kernel
        # < .5

        i, j = 5, 5
        kernel_size = 5
        array = np.ma.MaskedArray(data=np.full((10, 10), .5, dtype=np.float), mask=False)
        kernel = np.arange(kernel_size ** 2).reshape(kernel_size, kernel_size) / kernel_size ** 2

        kernel = np.ma.MaskedArray(data=kernel, mask=False)

        filters.habitat.apply_kernel_greater_than(array, i, j, kernel)

        # retained value, outside application area
        self.assertAlmostEqual(array[0, 0], 0.5)

        # new value, center of application area
        self.assertAlmostEqual(array[i, j], 0.5)

        # LR corner of kernel, should have kernel value:
        self.assertAlmostEqual(array[i + kernel_size // 2, j + kernel_size // 2], .96)

        # UL corner of kernel, should have original value since kernel value < .5
        self.assertAlmostEqual(array[i - kernel_size // 2, j - kernel_size // 2], .5)
