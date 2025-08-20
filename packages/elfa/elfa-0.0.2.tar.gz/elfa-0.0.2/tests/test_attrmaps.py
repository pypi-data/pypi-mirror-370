import unittest

import numpy as np

import elfa.attr_maps

np.random.seed(42)


class TestElfa(unittest.TestCase):

    def test_efam(self):
        WT = np.random.rand(8, 16)
        factors = np.random.rand(250, 8)
        act_shape = (5, 5)
        h_maxmin = elfa.attr_maps.efam_factors(
            WT, factors, act_shape, norm_method="max_min"
        )
        h_max = elfa.attr_maps.efam_factors(WT, factors, act_shape, norm_method="max")
        h_relu = elfa.attr_maps.efam_factors(WT, factors, act_shape, norm_method="relu")

        self.assertEqual(h_maxmin.shape, (10, 5, 5))
        self.assertEqual(h_max.shape, (10, 5, 5))
        self.assertEqual(h_relu.shape, (10, 5, 5))

        self.assertTrue(np.all(h_maxmin >= 0) and np.all(h_maxmin <= 1))
        self.assertTrue(np.all(h_max <= 1))
        self.assertTrue(np.all(h_relu >= 0) and np.all(h_relu <= 1))


if __name__ == "__main__":
    unittest.main()
